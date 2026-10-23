from load_basics import *
from nbodykit.source.catalog import BigFileCatalog
from nbodykit.lab import ArrayCatalog, FFTPower
import argparse

def gen_mesh(sdir):

    bf = BigFile(sdir)
    pos = bf["1/Position"][:]
    vel = bf["1/Velocity"][:]
    cat = ArrayCatalog({'Position' : pos, 'Velocity' : vel}, BoxSize=[Lbox, Lbox, Lbox])
    mesh = cat.to_mesh(resampler='cic',Nmesh=Nmesh,position='Position')
    return mesh

def downsize(one_plus_delta, factor):
    """
    Downsize the mesh by a factor of `factor`.
    """
    if factor == 1:
        return one_plus_delta
    elif factor < 1:
        raise ValueError("Downsize factor must be >= 1")
    
    new_shape = (one_plus_delta.shape[0] // factor, 
                 one_plus_delta.shape[1] // factor, 
                 one_plus_delta.shape[2] // factor)
    
    downsampled = one_plus_delta.reshape(new_shape[0], factor, \
        new_shape[1], factor, new_shape[2], factor).mean(axis=(1,3,5))
    return downsampled

def save_mesh(aval, delta, nmesh):
    ofile = f"{rundir}/delta_{aval}_{nmesh}.dat"
    delta.tofile(ofile)
    print(f"Saved mesh to {ofile}")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate and save mesh from simulation data.")
    parser.add_argument('--rundir', type=str, required=True, help='Output root directory')
    parser.add_argument('--Nmesh', type=int, help='Mesh resolution')
    parser.add_argument('--Lbox', type=float, help='Box size of the simulation')
    parser.add_argument('--downsample', type=int, default=1, help='Downsample factor for the mesh')
    args = parser.parse_args()

    rundir = args.rundir
    Nmesh = args.Nmesh
    Lbox = args.Lbox
    downsample = args.downsample

    flist = sorted(glob.glob(f"{rundir}/fastpm_*"))
    alist = [f.split('/')[-1].split('_')[-1] for f in flist]

    for snap, ifile in enumerate(flist):
        aval = alist[snap]
        print(f"Processing file {ifile} for snapshot {snap}", flush=True)
        mesh = gen_mesh(ifile)
        one_plus_delta = mesh.paint(mode='real').value
        # save original mesh
        save_mesh(aval, one_plus_delta - 1, Nmesh)
        if downsample > 1:
            one_plus_delta = downsize(one_plus_delta, downsample)
        save_mesh(aval, one_plus_delta - 1, Nmesh// downsample)

        


