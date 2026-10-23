-- parameter file
------ Size of the simulation -------- 

-- For Testing
nc = 128
boxsize = 400.0

-------- Time Sequence ----
-- linspace: Uniform time steps in a
-- time_step = linspace(0.025, 1.0, 39)
-- logspace: Uniform time steps in loga
-- time_step = linspace(0.01, 1.0, 10)
time_step = linspace(0.05, 1, 40)

output_redshifts= {0.0, 0.025, 0.051, 0.079, 0.108, 0.139, 0.171, 0.206, 0.242, 0.281, 0.322, 0.366, 0.413, 0.463, 0.518, 0.576, 0.639, 0.707, 0.781, 0.862, 0.95, 1.047, 1.155, 1.274, 1.407, 1.557, 1.727, 1.921, 2.145, 2.406, 2.714, 3.084, 3.535, 4.098, 4.821, 5.783, 7.125, 9.13, 12.448, 19.0}  -- redshifts of output

-- Cosmology --
Omega_m = 0.307494
h       = 0.6774

-- Start with a linear density field
-- Power spectrum of the linear density field: k P(k) in Mpc/h units
-- Must be compatible with the Cosmology parameter
read_powerspectrum= "/home/nianyic/FMsims/L400_n128_s40/powerspec.txt"
linear_density_redshift = 0.0 -- the redshift of the linear density field.
random_seed= **seed**
particle_fraction = 1.0
--
-------- Approximation Method ---------------
force_mode = "fastpm"
kernel_type = "gadget"

growth_mode = "LCDM"

pm_nc_factor = 2
lpt_nc_factor = 1

np_alloc_factor= 4.0      -- Amount of memory allocated for particle

-------- Output ---------------

-- Dark matter particle outputs (all particles)
write_snapshot= "/home/nianyic/scratch1/FMsims/L400_n128_s40/**run**/fastpm" 
-- 1d power spectrum (raw), without shotnoise correction
write_powerspectrum = "/home/nianyic/scratch1/FMsims/L400_n128_s40/**run**/powerspec"
write_whitenoisek = "/home/nianyic/scratch1/FMsims/L400_n128_s40/**run**/IC"
write_lineark = "/home/nianyic/scratch1/FMsims/L400_n128_s40/**run**/IC"
