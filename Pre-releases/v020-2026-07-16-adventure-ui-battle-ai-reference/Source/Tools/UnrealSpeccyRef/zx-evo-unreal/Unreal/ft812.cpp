
// FT812 VideoDAC2 wrapper

#include "std.h"
#include "vars.h"
#include "util.h"
#include "dxrend.h"
#include "resource.h"
#include <chrono>
#include <mutex>
#include "ft812.h"
#include "ft8xx/EVE_Platform.h"
#include "ft8xx/FT_Platform.h"

namespace vdac2
{
  HMODULE ft8xxemu_hdl = 0;

  typedef const char * (*BT8XXEMU_version_t)();
  typedef void (*BT8XXEMU_defaults_t)(uint32_t versionApi, BT8XXEMU_EmulatorParameters *params, BT8XXEMU_EmulatorMode mode);
  typedef void (*BT8XXEMU_run_t)(uint32_t versionApi, void **emulator, const BT8XXEMU_EmulatorParameters *params);
  typedef void (*BT8XXEMU_destroy_t)(void *emulator);
  typedef int (*BT8XXEMU_isRunning_t)(void *emulator);
  typedef void (*BT8XXEMU_chipSelect_t)(void *emulator, int cs);
  typedef uint8_t (*BT8XXEMU_transfer_t)(void *emulator, uint8_t data);
  typedef int (*BT8XXEMU_hasInterrupt_t)(void *emulator);

  BT8XXEMU_version_t BT8XXEMU_version;
  BT8XXEMU_defaults_t BT8XXEMU_defaults;
  BT8XXEMU_run_t BT8XXEMU_run;
  BT8XXEMU_destroy_t BT8XXEMU_destroy;
  BT8XXEMU_isRunning_t BT8XXEMU_isRunning;
  BT8XXEMU_chipSelect_t BT8XXEMU_chipSelect;
  BT8XXEMU_transfer_t BT8XXEMU_transfer;
  BT8XXEMU_hasInterrupt_t BT8XXEMU_hasInterrupt;

  void *pEmulator;

  HWND hw_wnd;
  HMENU menu;
  int wnd_width = 256;
  int wnd_height = 192;
  u32 bitmap[2048][2048];
  GDIBMP gdibmp = {{{sizeof(BITMAPINFOHEADER), 2048, -2048, 1, 32, BI_RGB, 0}}};

  // ---
  //  Since shitty FT8xx emulation lib has no interrupt support, we need to make a manual dusk.

  int addr_cnt = 0, data_cnt = 0;
  bool ss_int = false;
  bool has_irq = false;
  u32 addr_int = 0;
  std::mutex mtx;

  u8 xfer_int(u8 r, u8 d)
  {
    if (ss_int)
    {
      if (addr_cnt < 3)
      {
        addr_int = (addr_int << 8) | d;
        addr_cnt++;
      }

      else if (data_cnt < 2)
      {
        if (data_cnt == 1)
        {
          if (addr_int == 0x3020A8) // Interrupt events
          {
            mtx.lock();
            r = has_irq;
            has_irq = false;
            mtx.unlock();
          }
        }

        data_cnt++;
      }
    }

    return r;
  }

  void set_ss(bool ss)
  {
    BT8XXEMU_chipSelect(pEmulator, ss);

    ss_int = ss;
    if (!ss)
      addr_cnt = data_cnt = addr_int = 0;
  }

  bool is_interrupt()
  {
    static bool old_irq = false;
    bool rc;
    // rc = BT8XXEMU_hasInterrupt(pEmulator); // <- doesn't work ������ ��� ����� ��������� - �����

    mtx.lock();
    rc = has_irq && !old_irq;
    old_irq = has_irq;
    mtx.unlock();

    return rc;
  }

  u8 transfer(u8 d)
  {
    u8 r = BT8XXEMU_transfer(pEmulator, d);
    r = xfer_int(r, d);

    return r;
  }

  // HMM2 debug: по триггеру ftdump.req читает RAM_DL чипа по SPI → ftdump.bin (8К).
  // Вызывать ТОЛЬКО из потока эмуляции (input-poll), не из show_screen — иначе гонка SPI с Z80.
  void dump_ftstate()
  {
    FILE *rq = fopen("ftdump.req", "rb");
    if (!rq) return;
    // адрес из содержимого файла (hex), по умолчанию RAM_DL 0x300000
    char txt[32]; for (int k = 0; k < 32; k++) txt[k] = 0;
    size_t rn = fread(txt, 1, sizeof(txt) - 1, rq);
    fclose(rq);
    remove("ftdump.req");
    unsigned int addr = 0x300000;
    {
      unsigned int a = 0; bool any = false;
      for (int k = 0; k < (int)rn; k++) {
        char c = txt[k]; int dgt = -1;
        if (c >= '0' && c <= '9') dgt = c - '0';
        else if (c >= 'a' && c <= 'f') dgt = c - 'a' + 10;
        else if (c >= 'A' && c <= 'F') dgt = c - 'A' + 10;
        if (dgt >= 0) { a = (a << 4) | (unsigned)dgt; any = true; } else if (any) break;
      }
      if (any) addr = a;
    }

    static unsigned char buf[8192];
    // FT81x host-read: 3 байта адреса (bit23-22=00 => read) + 1 dummy + N байт.
    set_ss(true);
    transfer((addr >> 16) & 0x3F);
    transfer((addr >> 8) & 0xFF);
    transfer(addr & 0xFF);
    transfer(0);
    for (int i = 0; i < 8192; i++) buf[i] = transfer(0);
    set_ss(false);

    FILE *f = fopen("ftdump.bin", "wb");
    if (f) { fwrite(buf, 1, 8192, f); fclose(f); }
  }

  void close_ft8xx()
  {
    if (ft8xxemu_hdl)
    {
      BT8XXEMU_destroy(pEmulator);
      FreeLibrary(ft8xxemu_hdl);
      ft8xxemu_hdl = 0;
    }
  }

  void log(BT8XXEMU_Emulator *sender, void *context, BT8XXEMU_LogType type, const char *message)
  {
    if (type == BT8XXEMU_LogMessage)
      return;

    else if (type == BT8XXEMU_LogWarning)
      color(CONSCLR_WARNING);

    else if (type == BT8XXEMU_LogError)
      color(CONSCLR_ERROR);

    printf("%s\n", message);
  }

  static LRESULT APIENTRY WndProc(HWND hwnd, UINT uMessage, WPARAM wparam, LPARAM lparam)
  {
    PAINTSTRUCT ps;

    if (uMessage == WM_CLOSE)
    {
      return 0;
    }

    if (uMessage == WM_PAINT)
    {
      const auto bptr = bitmap;
      const auto hdc = BeginPaint(hwnd, &ps);
      SetDIBitsToDevice(hdc, 0, 0, wnd_width, wnd_height, 0, 0, 0, wnd_height, bptr, &gdibmp.header, DIB_RGB_COLORS);
      EndPaint(hwnd, &ps);
      return 0;
    }

    if (uMessage == WM_COMMAND)
    {
      // switch (wparam)
      // {
      // }
    }

    return DefWindowProc(hwnd, uMessage, wparam, lparam);
  }

  void set_window_size()
  {
    RECT cl_rect;
    const DWORD dw_style = WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX;

    cl_rect.left = 0;
    cl_rect.top = 0;
    cl_rect.right = wnd_width - 1;
    cl_rect.bottom = wnd_height - 1;
    AdjustWindowRect(&cl_rect, dw_style, GetMenu(hw_wnd) != nullptr);
    SetWindowPos(hw_wnd, HWND_BOTTOM, 0, 0, cl_rect.right - cl_rect.left + 1, cl_rect.bottom - cl_rect.top + 1, 0);
  }

  // --- HMM2 debug: дамп реального FT812-framebuffer в BMP для автономной верификации ---
  // Пишем атомарно (tmp+rename), троттлинг. argb8888 в памяти = BGRA → совместимо с 32bpp BMP.
  // Источник истины: это кадр самого чипа bt8xxemu, как на железе.
  void dump_framebuffer(const argb8888 *buffer, uint32_t w, uint32_t h)
  {
    static int ctr = 0;
    if ((ctr++ % 6) != 0) return;            // ~каждый 6-й кадр

#pragma pack(push, 1)
    struct BmpHdr {
      uint16_t bfType; uint32_t bfSize; uint16_t r1, r2; uint32_t bfOffBits;
      uint32_t biSize; int32_t biW, biH; uint16_t biPlanes, biBpp;
      uint32_t biComp, biSizeImg; int32_t biXppm, biYppm; uint32_t biClrUsed, biClrImp;
    } hdr;
#pragma pack(pop)
    uint32_t imgSize = w * h * 4;
    hdr.bfType = 0x4D42; hdr.r1 = hdr.r2 = 0; hdr.bfOffBits = sizeof(hdr);
    hdr.bfSize = sizeof(hdr) + imgSize;
    hdr.biSize = 40; hdr.biW = (int32_t)w; hdr.biH = -(int32_t)h;   // top-down
    hdr.biPlanes = 1; hdr.biBpp = 32; hdr.biComp = 0; hdr.biSizeImg = imgSize;
    hdr.biXppm = hdr.biYppm = 2835; hdr.biClrUsed = hdr.biClrImp = 0;

    FILE *f = fopen("ft812_dump.tmp", "wb");
    if (!f) return;
    fwrite(&hdr, sizeof(hdr), 1, f);
    fwrite(buffer, imgSize, 1, f);
    fclose(f);
    remove("ft812_dump.bmp");
    rename("ft812_dump.tmp", "ft812_dump.bmp");
  }

  // Window rendered callback
  int show_screen(BT8XXEMU_Emulator *sender, void *context, int output, const argb8888 *buffer, uint32_t hsize, uint32_t vsize, BT8XXEMU_FrameFlags flags)
  {
    static bool is_swap = false;

    if ((wnd_width != hsize) || (wnd_height != vsize))
    {
      wnd_width = hsize;
      wnd_height = vsize;
      set_window_size();
    }

    //printf("%0X\r\n", flags);

    if (flags & BT8XXEMU_FrameChanged)
      is_swap = true;

    if (is_swap && BT8XXEMU_FrameBufferComplete)
    {
      is_swap = false;
      dump_framebuffer(buffer, hsize, vsize);   // HMM2 debug: реальный кадр чипа → BMP
      mtx.lock();
      has_irq = true;
      mtx.unlock();

#if 0
      {
        static std::chrono::time_point<std::chrono::high_resolution_clock> old_time;
        auto new_time = std::chrono::high_resolution_clock::now();
        auto time = new_time - old_time;
        old_time = new_time;
        auto elapsed_us = time / std::chrono::microseconds(1);
        printf("%d us\r\n", elapsed_us);
      }
#endif

      u8 *s = (u8*) buffer;

      for (int y = 0; y < vsize; y++)
      {
        memcpy(bitmap[y], s, hsize * 4);
        s += 4 * hsize;
      }

      InvalidateRect(hw_wnd, nullptr, FALSE);
      PAINTSTRUCT ps;
      const auto hdc = BeginPaint(hw_wnd, &ps);
      SetDIBitsToDevice(hdc, 0, 0, wnd_width, wnd_height, 0, 0, 0, wnd_height, bitmap, &gdibmp.header, DIB_RGB_COLORS);
      EndPaint(hw_wnd, &ps);
      //std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    return 1;
  }

  int open_ft8xx(const char **ver)
  {
    if (ft8xxemu_hdl)
      return 0;

    ft8xxemu_hdl = LoadLibrary("bt8xxemu.dll");
    if (!ft8xxemu_hdl)
      return 1;

    BT8XXEMU_version = (BT8XXEMU_version_t)GetProcAddress(ft8xxemu_hdl, "BT8XXEMU_version");
    BT8XXEMU_defaults = (BT8XXEMU_defaults_t)GetProcAddress(ft8xxemu_hdl, "BT8XXEMU_defaults");
    BT8XXEMU_run = (BT8XXEMU_run_t)GetProcAddress(ft8xxemu_hdl, "BT8XXEMU_run");
    BT8XXEMU_destroy = (BT8XXEMU_destroy_t)GetProcAddress(ft8xxemu_hdl, "BT8XXEMU_destroy");
    BT8XXEMU_isRunning = (BT8XXEMU_isRunning_t)GetProcAddress(ft8xxemu_hdl, "BT8XXEMU_isRunning");
    BT8XXEMU_chipSelect = (BT8XXEMU_chipSelect_t)GetProcAddress(ft8xxemu_hdl, "BT8XXEMU_chipSelect");
    BT8XXEMU_transfer = (BT8XXEMU_transfer_t)GetProcAddress(ft8xxemu_hdl, "BT8XXEMU_transfer");
    BT8XXEMU_hasInterrupt = (BT8XXEMU_hasInterrupt_t)GetProcAddress(ft8xxemu_hdl, "BT8XXEMU_hasInterrupt");

    BT8XXEMU_EmulatorParameters emulatorParams;
    BT8XXEMU_defaults(BT8XXEMU_VERSION_API, &emulatorParams, BT8XXEMU_EmulatorFT812);

    emulatorParams.Graphics = show_screen;
    emulatorParams.Log = log;
    emulatorParams.Flags = BT8XXEMU_EmulatorEnableAudio
                         | BT8XXEMU_EmulatorEnableCoprocessor
                         | BT8XXEMU_EmulatorEnableGraphicsMultithread;
    emulatorParams.Flags &= (~BT8XXEMU_EmulatorEnableDynamicDegrade & ~BT8XXEMU_EmulatorEnableRegPwmDutyEmulation);

    BT8XXEMU_run(BT8XXEMU_VERSION_API, &pEmulator, &emulatorParams);

    WNDCLASS  wc{};
    const DWORD dw_style = WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX;

    wc.lpfnWndProc = WNDPROC(WndProc);
    wc.hInstance = hIn;
    wc.lpszClassName = "FT_WND";
    wc.hIcon = LoadIcon(hIn, MAKEINTRESOURCE(IDI_MAIN));
    wc.hCursor = LoadCursor(nullptr, IDC_ARROW);
    RegisterClass(&wc);

    // visuals_menu = LoadMenu(hIn, MAKEINTRESOURCE(IDR_DEBUGMENU)); // !!!

    hw_wnd = CreateWindow("FT_WND", "VDAC2 Emul", dw_style, CW_USEDEFAULT, CW_USEDEFAULT, 0, 0, nullptr, menu, hIn, NULL);
    set_window_size();

    if (!BT8XXEMU_isRunning(pEmulator))
    {
      close_ft8xx();
      return 2;
    }

    ShowWindow(hw_wnd, SW_SHOW);
    set_window_size();

    *ver = BT8XXEMU_version();

    return 0;
  }
}
