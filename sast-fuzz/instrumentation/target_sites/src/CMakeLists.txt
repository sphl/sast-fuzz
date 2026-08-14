llvm_map_components_to_libnames(LLVM_LIBS
    analysis
    bitwriter
    instrumentation
    irreader
)

add_library(libcbi STATIC container/target.cpp)
target_include_directories(libcbi PUBLIC "${CBI_INCLUDE_DIR}")
target_compile_options(libcbi PUBLIC
    $<$<CONFIG:Debug>:-g>
    $<$<CONFIG:Debug>:-O0>
    $<$<NOT:$<CONFIG:Debug>>:-O3>
)
target_compile_definitions(libcbi PUBLIC
    $<$<CONFIG:Debug>:CBI_DEBUG>
    $<$<NOT:$<CONFIG:Debug>>:NDEBUG>
)
set_target_properties(libcbi PROPERTIES PREFIX "")

add_executable(cbi main.cpp)
target_include_directories(cbi PRIVATE ${SVF_INCLUDE_DIRS} ${LLVM_INCLUDE_DIRS})
target_compile_options(cbi PRIVATE -fno-rtti -fPIC)
target_link_libraries(cbi PRIVATE libcbi ${SVF_LIB} ${SVF_CUDD_LIB} ${LLVM_LIBS})
