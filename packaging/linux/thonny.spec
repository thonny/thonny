%global srcname thonny

Name:           %{srcname}
Version:        2.1.12
Release:        1%{?dist}
Summary:        Python IDE for beginners

License:        MIT
URL:            http://thonny.org
Source0:        https://pypi.python.org/packages/01/ad/b9ce07063b9d6b9c5f3835b0256775feacd75de44d86f813924ee96d3f16/thonny-2.1.12.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  desktop-file-utils
Requires:       python3 >= 3.4
Requires:       python3-tkinter
Requires:       python3-pip
Requires:       python3-jedi >= 0.9

%description
Thonny is a simple Python IDE with features useful for learning programming.

%prep
%autosetup -n %{srcname}-%{version}


%build
%py3_build


%install
%py3_install


%files
%license LICENSE.txt
%doc README.rst
%{python3_sitelib}/*
%{_bindir}/thonny



%changelog
* Mon Oct 16 2017 Aivar Annamaa <aivar.annamaa@gmail.com>
- Initial package
