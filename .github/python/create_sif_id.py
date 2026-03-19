import io

from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem


def make_sif_asset():

    # Prepare the platform
    plat_obj = Platform(type='COMPS',
                        endpoint='https://comps.idmod.org',
                        environment='Calculon')

    # Definition content
    file_text = io.StringIO()

    file_text.write('Bootstrap: docker                                                     \n')
    file_text.write('From: rockylinux/rockylinux:9.6                                       \n')
    file_text.write('                                                                      \n')
    file_text.write('%post                                                                 \n')
    file_text.write('    dnf -y upgrade                                                    \n')
    file_text.write('    dnf -y install python3.9                                          \n')
    file_text.write('    dnf -y install python3.9-pip                                      \n')
    file_text.write('    dnf -y install mpich                                              \n')
    file_text.write('    dnf clean all                                                     \n')
    file_text.write('                                                                      \n')
    file_text.write('    python3.9 -m pip install pip --upgrade                            \n')
    file_text.write('    python3.9 -m pip install numpy                                    \n')
    file_text.write('                                                                      \n')
    file_text.write('%environment                                                          \n')
    file_text.write('    export PATH=$PATH:/usr/lib64/mpich/bin                            \n')
    file_text.write('    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib64/mpich/lib      \n')
    file_text.write('                                                                      \n')

    # Creates a work item to build image
    sbwi_obj = SingularityBuildWorkItem(name='Build_SIF_Image',
                                        definition_content=file_text.getvalue(),
                                        force=True)

    # Wait until the image is built
    ac_obj = sbwi_obj.run(wait_until_done=True,
                          platform=plat_obj)

    # Save asset id for sif to file
    ac_obj.to_id_file('sif_file.id')

    return None


if __name__ == '__main__':
    make_sif_asset()
