#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <vector>
#include "fpng.h"
#include <mutex>

namespace py = pybind11;

// std::mutex init_lock;

void init()
{
    // const std::lock_guard<std::mutex> lock(init_lock);
    fpng::fpng_init();
}

py::array_t<uint8_t> fpng_encode_image_to_memory(py::array_t<uint32_t> pImage, uint32_t num_chans, uint32_t flags = 0)
{
    // init();
    auto v = new std::vector<uint8_t>();
    bool success = fpng::fpng_encode_image_to_memory(pImage.data(), pImage.shape(1), pImage.shape(0), num_chans, *v, flags);
    if (!success)
        return py::array();
    //ensures the vector is deleted when the python object is deleted
    auto capsule = py::capsule(v, [](void *v) { delete reinterpret_cast<std::vector<int>*>(v);});
    //returns the data without copying
    return py::array(v->size(), v->data(), capsule);
}

bool fpng_cpu_supports_sse41()
{
    return fpng::fpng_cpu_supports_sse41();
}

// py::array_t<uint32_t> fpng_decode_image_from_memory(py::array_t<uint8_t> )
// {

// }

PYBIND11_MODULE(fpng, m) {
    init();
    m.doc() = "fpng wrapper"; // optional module docstring
    m.def("encode_image_to_memory", &fpng_encode_image_to_memory, "encodes an image to memory");
    // m.def("decode_image_from_memory", &fpng_decode_image_from_memory, "decodes an image from memory");
    m.def("cpu_supports_sse41", &fpng_cpu_supports_sse41, "tests whether CPU supports SSE41");
}