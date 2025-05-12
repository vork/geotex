#include <geogram/basic/common.h>
#include <geogram/mesh/mesh.h>
#include <geogram/mesh/mesh_io.h>
#if __has_include(<geogram/parameterization/mesh_atlas_maker.h>)
#  include <geogram/parameterization/mesh_atlas_maker.h>
#else
#  include <geogram/mesh/parameterization/mesh_atlas_maker.h>
#endif
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;
using GEO::Mesh;

/* ---------- helpers ---------------------------------------------------- */
static void numpy_to_mesh(py::array_t<double, py::array::c_style> V,
                         py::array_t<uint32_t, py::array::c_style> F,
                         Mesh& M) {
    GEO::initialize();
    auto v   = V.unchecked<2>();   // (n,3)
    auto f   = F.unchecked<2>();   // (m,3)

    M.vertices.set_dimension(3);
    M.vertices.create_vertices(v.shape(0));
    for (size_t i=0; i<v.shape(0); ++i) {
        M.vertices.point(i) = GEO::vec3(v(i,0), v(i,1), v(i,2));
    }
    M.facets.create_triangles(f.shape(0));
    for (size_t i=0; i<f.shape(0); ++i) {
        for (int k=0; k<3; ++k) M.facets.set_vertex(i,k,f(i,k));
    }
}

static py::array_t<double> make_uv_numpy(Mesh &M) {
    GEO::Attribute<double> uv;
    uv.bind(M.facet_corners.attributes(), "tex_coord");
    if(!uv.is_bound()) throw std::runtime_error("atlas failed – no tex_coord");

    size_t nc = M.facet_corners.nb();           // 3 × #triangles
    std::vector<size_t> shape = {nc, 2};
    py::array_t<double> out(shape);
    auto r = out.mutable_unchecked<2>();
    for(size_t i=0; i<nc; ++i) {
        r(i,0) = uv[2*i];
        r(i,1) = uv[2*i+1];
    }
    return out;
}

/* ---------- Python API -------------------------------------------------- */
PYBIND11_MODULE(geotex, m) {
    m.doc() = "Minimal bindings to Geogram texturing.";

    m.def("make_atlas",
        [](py::array V, py::array F,
           double hard=45.0,
           std::string param="ABF",
           std::string pack ="xatlas",
           bool verbose=false) {
            Mesh M;
            numpy_to_mesh(V, F, M);

            GEO::ChartParameterizer p =
                (param=="lscm")?   GEO::PARAM_LSCM :
                (param=="spectral_lscm")? GEO::PARAM_SPECTRAL_LSCM :
                GEO::PARAM_ABF;

            GEO::ChartPacker pk =
                (pack=="tetris") ? GEO::PACK_TETRIS : GEO::PACK_XATLAS;

            GEO::mesh_make_atlas(M, hard, p, pk, verbose);
            return make_uv_numpy(M);
        },
        py::arg("vertices"),
        py::arg("faces"),
        py::arg("hard_angles_threshold") = 45.0,
        py::arg("parameterizer") = "abf",
        py::arg("packer") = "xatlas",
        py::arg("verbose") = false
    );
}
