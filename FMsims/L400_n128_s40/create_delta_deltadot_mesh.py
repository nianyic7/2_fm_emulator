from load_basics import *
from nbodykit.lab import *
from nbodykit.lab import ArrayCatalog, FFTPower
import h5py, glob
# from astrid_utils import *
from astropy.cosmology import Planck15 as cosmo
from astropy import units
import argparse
import os

def gen_mesh_g4(fdir , Lbox=400, Nmesh=128, comp=False):
    bf = h5py.File(fdir, "r")
    aa = bf["Header"].attrs['Time']
    zz = 1/aa - 1
    pos = bf["PartType1/Coordinates"][:]
    cat = ArrayCatalog({'Position' : pos}, BoxSize=[Lbox, Lbox, Lbox])
    mesh_rho = cat.to_mesh(compensated=comp, resampler='tsc',Nmesh=Nmesh,position='Position', interlaced=True)
    return mesh_rho, zz


def process_triplet(triplet):
    snap0, snap1, snap2 = triplet
    mesh0, z0 = gen_mesh_g4(snap0, Lbox=args.Lbox, Nmesh=args.Nmesh, comp=True)
    mesh1, z1 = gen_mesh_g4(snap1, Lbox=args.Lbox, Nmesh=args.Nmesh, comp=True)
    mesh2, z2 = gen_mesh_g4(snap2, Lbox=args.Lbox, Nmesh=args.Nmesh, comp=True)
    a0, a1, a2 = 1/(1+z0), 1/(1+z1), 1/(1+z2)
    # compute deltadot
    delta0 = (mesh0.paint(mode='real').value -1)
    delta1 = (mesh1.paint(mode='real').value -1)
    delta2 = (mesh2.paint(mode='real').value -1)
    deltadot = (delta2 - delta1) / (a2 - a1)
    return delta1, deltadot, a0, a1, a2



if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--root', type=str, help='input root')
    argparser.add_argument('--Lbox', type=float, default=400, help='box size')
    argparser.add_argument('--Nmesh', type=int, default=128, help='mesh size')
    argparser.add_argument('--runname', type=str, required=True, help='run name')

    args = argparser.parse_args()
    rundir = args.root + "/" + args.runname + "/"
    outdir = rundir + "mesh/"
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    reverse_index = np.loadtxt(rundir + "reverse_index.txt").astype(int)
    snapfiles = sorted(glob.glob(rundir + "output/snap_0*.hdf5"))
    snapfiles = [snapfiles[i] for i in reverse_index]

    i = 0
    alist = []
    while i < len(snapfiles) - 2:
        triplet = (snapfiles[i], snapfiles[i+1], snapfiles[i+2])
        delta, deltadot, a0, a1, a2 = process_triplet(triplet)
        np.save(outdir + f"delta_N{args.Nmesh}_a{a1:.6f}.npy", delta)
        np.save(outdir + f"deltadot_N{args.Nmesh}_a{a1:.6f}.npy", deltadot)
        i += 3
        alist += [a0, a1, a2]
        print(f"Processed triplet {i//3} with a0={a0:.6f}, a1={a1:.6f}, a2={a2:.6f}", flush=True)

    alist = np.array(alist)
    np.savetxt(rundir + "output-a-list.txt", alist)
    print(f"Done with run {args.runname}, saved output to {outdir}", flush=True)

