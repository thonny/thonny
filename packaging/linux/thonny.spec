Name:           thonny
Version:        2.1.12
Release:        1%{?dist}
Summary:        Python IDE for beginners

License:        MIT
URL:            http://thonny.org
Source0:        https://pypi.python.org/packages/01/ad/b9ce07063b9d6b9c5f3835b0256775feacd75de44d86f813924ee96d3f16/thonny-2.1.12.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  desktop-file-utils
Requires:       python3 
Requires:       python3-tkinter
Requires:       python3-pip
Requires:       python3-jedi

%description
Thonny is a simple Python IDE with features useful for learning programming.

%prep
%autosetup -n %{name}-%{version}


%build
%py3_build


%install
%py3_install

mkdir -p %{buildroot}/%{_datadir}/applications/
cat > %{buildroot}/%{_datadir}/applications/Thonny.desktop <<-EOF
[Desktop Entry]
Type=Application
Name=Thonny
GenericName=Python IDE
Exec=%{_bindir}/%{name} %F
Comment=Python IDE for beginners
Icon=%{python3_sitelib}/%{name}/res/thonny.png
StartupWMClass=Thonny
StartupNotify=true
Terminal=false
Categories=Education;Development
MimeType=text/x-python;
Actions=Edit;

[Desktop Action Edit]
Exec=%{_bindir}/%{name} %F
Name=Edit with Thonny
EOF

desktop-file-validate %{buildroot}/%{_datadir}/applications/Thonny.desktop



%files
%license LICENSE.txt
%doc README.rst
%{python3_sitelib}/*
%{_bindir}/thonny
%{_datadir}/applications/Thonny.desktop



%changelog
* Mon Oct 16 2017 Aivar Annamaa <aivar.annamaa@gmail.com>
- Initial package
