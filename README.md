 # Signing kernel modules and EFI binaries in the Open Build Service

RPM packages that need to sign files during build should add the following lines
to the specfile

```
# needssslcertforbuild
export BRP_PESIGN_FILES='pattern...'
BuildRequires: pesign-obs-integration
```

BRP_PESIGN_PACKAGES can optionally be defined to restrict repacking to a subset
of packages of choice.

Debian packages need to add the following line to the Source stanza in the
debian/control file, which will add "Obs: needssslcertforbuild" to the generated
.dsc file:

```XS-Obs: needssslcertforbuild```

The "# needssslcertforbuild" comment tells the buildservice to store the
signing certificate in %_sourcedir/_projectcert.crt. At the end of the
install phase, the brp-99-pesign script computes hashes of all
files matching the patterns in $BRP_PESIGN_FILES. The sha256 hashes are stored
in %_topdir/OTHER/%name.cpio.rsasign, plus the script places a
pesign-repackage.spec file there. When the first rpmbuild finishes, the
buildservice sends the cpio archive to the signing server, which returns
a rsasigned.cpio archive with RSA signatures of the sha256 hashes.

The pesign-repackage.spec takes the original RPMs, unpacks them and
appends the signatures to the files. It then uses the
pesign-gen-repackage-spec script to generate another specfile, which
builds new RPMs with signed files. The supported file types are:

- *.ko
    - Signature appended to the module
- efi binaries
    - Signature embedded in a header. If a HMAC checksum named
      .$file.hmac exists, it is regenerated
- db, KEK and PK auth files
    - The pkcs#7 SignedData signature embedded in the EFI_VARIABLE_AUTHENTICATION_2
      header of the final auth file.

Debian packages can use the dh-signobs debhelper to automate signing and
repacking. Build-depend on dh-signobs and add --with signobs to the dh line
in debian/rules to use the fully automated helper.
Consult the dh_signobs manpage for more information.

## Options

### Kernel Module Compression
When BRP_PESIGN_COMPRESS_MODULE is passed, the script tries to compress the
kernel modules at the repackaging phase. Currently none, xz, gzip and zstd format is supported.
For enable the compression feature, put the following along with
BRP_PESIGN_FILES setup:

```export BRP_PESIGN_COMPRESS_MODULE="xz"```

### Dependency Generation
If you need macros within the pesign-repackage specfile to adjust [dependency generation](https://rpm-software-management.github.io/rpm/manual/dependency_generators.html)
, then place these in a source file called pesign-spec-macros, this will subseqently be loaded.

Example of pesign-spec-macros:

```%__kmp_supplements %_sourcedir/my-find-supplements %_sourcedir/pci_ids-%{version}```

To save creating duplicate copies of macros, load this file from your existing spec file by using the following:

```%{load:%{_sourcedir}/pesign-spec-macros}```

If you need some source files such as dependency generation scripts then place the names of these source files in a source file called pesign-copy-sources.

Example of pesign-copy-sources:
```
my-find-supplements
pci_ids-%{version}
```
## Examples

### signing db, KEK and PK auth files

Here is an example for signing a ESL (EFI_SIGNATURE_LIST) through open build service. It will produce a auth file. e.g. a KEK.auth.

```
%build
# https://github.com/microsoft/secureboot_objects/issues/157
export TIMESTAMP="2010-03-06 19:17:21"

# Generate signable binary file as the source file for signing
# Set timestamp and EFI_VARIABLE_APPEND_WRITE attribute
sign-efi-sig-list -t "$TIMESTAMP" -a -o KEK MicrosoftAndThirdParty/Firmware/KEK.bin KEK.auth

%install
export BRP_PESIGN_FILES='%{_sysconfdir}/uefi/certs/KEK.auth'
```

In the above case, the KEK.bin is ESL file a which is from Microsoft's secureboot object repo:
```
URL:            https://github.com/microsoft/secureboot_objects/releases
# x64, sha256:624c8629f4aab631064fde7d098ad60204288267b6e6edaab50a852ba7dd382b
Source0:        https://github.com/microsoft/secureboot_objects/releases/download/v%{version}/edk2-x64-secureboot-binaries.tar.gz
# aarch64, sha256:bf5a51e79815698013b9a062d489235cd042d0b1f9370a0a7c27a05367c95ed3
Source1:        https://github.com/microsoft/secureboot_objects/releases/download/v%{version}/edk2-aarch64-secureboot-binaries.tar.gz
```

The first 'sign-efi-sig-list -o' command will produce a signable binary file as the source file for signing to signing server:
```
man sign-efi-sig-list
       -o     Do not sign, but output a file of the exact bundle to be signed
```
Please note that the timestamp is a fixed '2010-03-06 19:17:21' value. The reason for Microsoft using it is in the issue#157 of Microsoft's secureboot_objects repo as the above URL.

The format of signable binary file (intput source):
```
KEK.signable.bin
[ Variable Name ][   Vendor GUID  ][   Attributes  ][    EFI_TIME    ][ Payload (ESL) ]
|<-- N bytes -->||<-- 16 bytes -->||<-- 4 bytes -->||<-- 16 bytes -->||<-- N bytes -->|
                 |<------------------- Fixed 36 bytes -------------->|
```
We named the KEK.signable.bin as KEK.auth in our example because pesign-repackage.spec.in will attach PKCS#7 SignedData signature back to the same file. So we direct named the source file as the target file.

The format of target file (output):
```
KEK.auth
[    EFI_TIME    ][WIN_CERTIFICATE][    CertType    ][ Signature (PKCS#7 SignedData) ][    Payload (ESL)    ]
|<-- 16 bytes -->||<-- 8 bytes -->||<-- 16 bytes -->||<---------- N bytes ---------->||<----- N bytes ----->|
|<------------- Fixed 40 bytes header ------------->||<------------------- Variable size ------------------>|
                  |<------------------ WIN_CERTIFICATE_UEFI_GUID ------------------->|
|<-------------------------- EFI_VARIABLE_AUTHENTICATION_2 ------------------------->|
```
For more detail, please check the latest UEFI spec.
