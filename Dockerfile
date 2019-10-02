# VERSION           4

# Build
FROM base/archlinux:latest as builder
MAINTAINER Tiago de Paula Peixoto <tiago@skewed.de>

RUN echo 'Server=https://archive.archlinux.org/repos/2019/07/14/$repo/os/$arch' > /etc/pacman.d/mirrorlist

RUN pacman-key --refresh-keys
RUN pacman -Suy --noconfirm
RUN pacman -S binutils make gcc fakeroot --noconfirm --needed
RUN pacman -S expac yajl git --noconfirm --needed
RUN pacman -S sudo grep file --noconfirm --needed

RUN pacman -S sudo boost python3 python3-scipy python-numpy \
              cgal cairomm python-cairo sparsehash cairomm   \
	      autoconf-archive pkg-config --noconfirm --needed

ENV MAKEPKG_USER=mkpkg \
    MAKEPKG_GROUP=mkpkg \
    MAKEPKG_ROOT=/tmp/build

RUN groupadd "${MAKEPKG_USER}" \
    && useradd -g "${MAKEPKG_GROUP}" "${MAKEPKG_USER}"

RUN mkdir -p ${MAKEPKG_ROOT}; chown mkpkg:mkpkg ${MAKEPKG_ROOT}

WORKDIR ${MAKEPKG_ROOT}

USER ${MAKEPKG_USER}
RUN curl -o PKGBUILD https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=python-graph-tool
RUN makepkg PKGBUILD --needed CXXFLAGS="-mtune=generic -O3 -pipe -flto=4 -ffunction-sections -fdata-sections" LDFLAGS="-Wl,--gc-sections"

USER root
RUN mv -v "${MAKEPKG_ROOT}/"python-graph-tool-*-x86_64.pkg.tar.xz /tmp/python-graph-tool.pkg.tar.xz

# Non-build

FROM base/archlinux:latest
RUN echo 'Server=https://archive.archlinux.org/repos/2019/07/14/$repo/os/$arch' > /etc/pacman.d/mirrorlist

COPY --from=builder /tmp/python-graph-tool.pkg.tar.xz /var/cache/pacman/pkg/python-graph-tool.pkg.tar.xz

RUN pacman -Sy archlinux-keyring --noconfirm
RUN pacman-key --refresh-keys
RUN pacman -Suy --noconfirm \
 && pacman -U --noconfirm --noprogressbar --needed \
    /var/cache/pacman/pkg/python-graph-tool.pkg.tar.xz \
 && yes | pacman -Scc --noconfirm

RUN pacman -S ipython gtk3 python-gobject python-matplotlib python-pandas jupyter-notebook mathjax python-cairocffi pandoc --noconfirm --needed

RUN useradd -m -g users user

ENV PYTHONIOENCODING=utf8
