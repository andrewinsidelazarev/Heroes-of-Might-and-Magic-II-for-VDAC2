#include <cstddef>
#include <iostream>
#include <set>
#include <tuple>

#include "map_object_info.h"

namespace MP2
{
    bool isOffGameActionObject( const MapObjectType objectType )
    {
        return ( objectType & OBJ_ACTION_OBJECT_TYPE ) == OBJ_ACTION_OBJECT_TYPE;
    }
}

int main()
{
    std::set<std::tuple<int, unsigned, int, int, int>> rows;

    for ( size_t group = 0; group < static_cast<size_t>( Maps::ObjectGroup::GROUP_COUNT ); ++group ) {
        const auto & objects = Maps::getObjectsByGroup( static_cast<Maps::ObjectGroup>( group ) );
        for ( const auto & object : objects ) {
            for ( const auto & part : object.groundLevelParts ) {
                rows.emplace( static_cast<int>( part.icnType ), part.icnIndex, static_cast<int>( part.layerType ), static_cast<int>( part.objectType ), 0 );
            }
            for ( const auto & part : object.topLevelParts ) {
                rows.emplace( static_cast<int>( part.icnType ), part.icnIndex, 0, static_cast<int>( part.objectType ), 1 );
            }
        }
    }

    std::cout << "icn,index,layer,object_type,top\n";
    for ( const auto & row : rows ) {
        std::cout << std::get<0>( row ) << ',' << std::get<1>( row ) << ',' << std::get<2>( row ) << ',' << std::get<3>( row ) << ',' << std::get<4>( row ) << '\n';
    }

    return 0;
}
