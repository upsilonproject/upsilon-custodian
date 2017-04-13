%include SPECS/.buildid.rpmmacro

Name:		upsilon-custodian
Version:	%{version_formatted_short}
Release:	%{timestamp}.%{?dist}
Summary:	Monitoring software
BuildArch: 	noarch

Group:		Applications/System
License:	GPLv2
URL:		http://upsilon-project.co.uk
Source0:	upsilon-custodian.zip

BuildRequires:	python
Requires:	python, upsilon-pycommon

%description
Monitoring software

%prep
%setup -q -n upsilon-custodian-%{tag}


%build
mkdir -p %{buildroot}/usr/share/upsilon-custodian/
cp src/* %{buildroot}/usr/share/upsilon-custodian/

mkdir -p %{buildroot}/etc/upsilon-custodian/
cp etc/* %{buildroot}/etc/upsilon-custodian/

mkdir -p %{buildroot}/usr/lib/systemd/system/
cp var/upsilon-custodian.service %{buildroot}/usr/lib/systemd/system/

%files
/usr/share/upsilon-custodian/*
/etc/upsilon-custodian/*
/usr/lib/systemd/system/upsilon-custodian.service
