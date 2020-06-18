from conans import ConanFile, CMake, tools
import os


class LibnameConan(ConanFile):
    name = "libname"
    description = "Keep it short"
    topics = ("conan", "libname", "logging")
    url = "https://github.com/bincrafters/conan-libname"
    homepage = "https://github.com/original_author/original_lib"
    license = "MIT"  # Indicates license type of the packaged library; please use SPDX Identifiers https://spdx.org/licenses/
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    requires = (
        "zlib/1.2.11"
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_TESTS"] = False  # example
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can just remove the lines below
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "PostgreSQL"
        self.cpp_info.names["cmake_find_package_multi"] = "PostgreSQL"
        self.env_info.PostgreSQL_ROOT = self.package_folder

        self.cpp_info.components.libs = [self._construct_library_name("pq")]

#        if self.options.with_zlib:
#            self.cpp_info.components.requires.append("zlib::zlib")

#        if self.options.with_openssl:
#            self.cpp_info.components.requires.append("openssl::openssl")

        if not self.options.shared:
            if self.settings.compiler == "Visual Studio":
                if tools.Version(self.version) < '12':
                    self.cpp_info.components.libs = ["libpgport"]
                else:
                    self.cpp_info.components.libs = ["libpgcommon"]
                    self.cpp_info.components.libs = ["libpgport"]
            else:
                if tools.Version(self.version) < '12':
                    self.cpp_info.components.libs = ["pgcommon"]
                    self.cpp_info.components.requires.extend(["pgcommon"])
                else:
                    self.cpp_info.components.libs = ["pgcommon", "pgcommon_shlib"]
                    self.cpp_info.components.libs = ["pgport", "pgport_shlib"]

        if self.settings.os == "Linux":
            self.cpp_info.components.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components.system_libs = ["ws2_32", "secur32", "advapi32", "shell32", "crypt32", "wldap32"]
