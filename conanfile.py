import shutil

from conans import ConanFile
from conans import tools
from conans.errors import ConanException


class GrpcConan(ConanFile):
    name = "grpc"
    version = "1.0.1"

    url = "https://github.com/sourcedelica/conan-grpc"
    settings = "os", "compiler", "build_type", "arch"
    license = "Three-clause BSD"
    description = "RPC library from Google based on Protobuf"
    generators = "cmake"
    exports = "change_dylib_names.sh"
    _source_dir = "grpc"

    def config_options(self):
        if self.settings.compiler == 'gcc' and float(self.settings.compiler.version.value) >= 5.1:
            if self.settings.compiler.libcxx != 'libstdc++11':
                raise ConanException("You must use the setting compiler.libcxx=libstdc++11")

    def source(self):
        self.run("git clone https://github.com/grpc/grpc.git --branch v%s --depth 1" 
                 % self.version, 
                 cwd=self._source_dir)
        self.run("git submodule update --init", cwd=self._source_dir)
        shutil.copy("change_dylib_names.sh", self._source_dir)

    def build(self):
        cpus = tools.cpu_count()
        # TODO - remove this after https://github.com/grpc/grpc/pull/8274 is fixed
        command_line_env = "CPPFLAGS='-DOSATOMIC_USE_INLINED=1'" if self.settings.os == "Macos" else ""
        self.run("%s make -j %s" % (command_line_env, cpus), cwd=self._source_dir)

    def package(self):
        if self.settings.os == "Macos":
            # Change *.dylib dependencies and ids to be relative to @executable_path
            self.run("bash change_dylib_names.sh", cwd=self._source_dir)

        self.copy("*.h",     dst="include", src="%s/include" % self._source_dir)
        self.copy("*.a",     dst="lib",     src="%s/libs/opt" % self._source_dir)
        self.copy("*.lib",   dst="lib",     src="%s/libs/opt" % self._source_dir)
        self.copy("*.dylib", dst="lib",     src="%s/libs/opt" % self._source_dir)
        self.copy("*.so*",   dst="lib",     src="%s/libs/opt" % self._source_dir)
        self.copy("*",       dst="bin",     src="%s/bins/opt" % self._source_dir)

    def package_info(self):
        # TODO: This should be customized based on options like secure:True, reflection:True
        self.cpp_info.libs = ["boringssl", "gpr",
                              "grpc++", "grpc++_unsecure", "grpc++_reflection",
                              "grpc", "grpc_unsecure"]

