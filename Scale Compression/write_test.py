import os
import shutil
import time
import hdf5plugin
from numcodecs import Blosc
import h5py
import numpy as np
import zarr
from netCDF4 import Dataset


def write(file_format, filename, num_datasets, dimensions):
    # Create a file with the specified number of datasets and populate each dataset with data from a generated array
    dataset_creation_time = 0.0
    dataset_population_time = 0.0

    # Create files
    if file_format == 'HDF5':
        file = h5py.File(f'files_1/{filename}.hdf5', 'w')
    elif file_format == 'HDF5_compressed':
        file = h5py.File(f'files_1/{filename}_compressed.hdf5', 'w')
    elif file_format == 'netCDF4':  # netCDF4 dimensions must be assigned upon file creation
        file = Dataset(f'files_1/{filename}.netc', 'w', format='NETCDF4')
        if len(dimensions) == 1:
            file.createDimension('x', None)
            axes = ('x',)
        elif len(dimensions) == 2:
            file.createDimension('x', None)
            file.createDimension('y', None)
            axes = ('x', 'y',)
        else:
            file.createDimension('x', None)
            file.createDimension('y', None)
            file.createDimension('z', None)
            axes = ('x', 'y', 'z')
    elif file_format == "netCDF4_compressed":
        file = Dataset(f'files_1/{filename}_compressed.netc', 'w', format='NETCDF4')
        if len(dimensions) == 1:
            file.createDimension('x', None)
            axes = ('x',)
        elif len(dimensions) == 2:
            file.createDimension('x', None)
            file.createDimension('y', None)
            axes = ('x', 'y',)
        else:
            file.createDimension('x', None)
            file.createDimension('y', None)
            file.createDimension('z', None)
            axes = ('x', 'y', 'z')
    
    elif file_format == 'Zarr':
        file = zarr.open(f'files_1/{filename}.zarr', 'w')
    elif file_format == 'Zarr_compressed': 
        file = zarr.open(f'files_1/{filename}_compressed.zarr', 'w')


    #Create datasets
    for i in range(0, num_datasets):      
        if file_format == 'HDF5':
            t1 = time.perf_counter()
            dataset = file.create_dataset(f'Dataset_{i}', shape=dimensions, dtype='f')
        if file_format == 'HDF5_compressed':
            t1 = time.perf_counter()
            dataset = file.create_dataset(f'Dataset_{i}', shape=dimensions, dtype='f', **hdf5plugin.Blosc(cname='zstd', clevel=9, shuffle=Blosc.SHUFFLE))
        if file_format == 'Zarr':
            t1 = time.perf_counter()
            dataset = file.create_dataset(f'Dataset_{i}', shape=dimensions, dtype='f')
        if file_format == 'Zarr_compressed':
            t1 = time.perf_counter()
            dataset = file.create_dataset(f'Dataset_{i}', shape=dimensions, dtype='f', compressor=Blosc(cname='zstd', clevel=9, shuffle=Blosc.SHUFFLE))
        if file_format == 'netCDF4':
            t1 = time.perf_counter()
            dataset = file.createVariable(f'Dataset_{i}', dimensions=axes, datatype='f')
        if file_format == 'netCDF4_compressed':
            t1 = time.perf_counter()
            dataset = file.createVariable(f'Dataset_{i}', dimensions=axes, datatype='f',compression='blosc_zstd')
        t2 = time.perf_counter()


    for i in range(num_datasets):
        #random data
        data = generate_array(tuple(dimensions))
        
        #retrieve the dataset
        if file_format == 'HDF5' or file_format == 'HDF5_compressed':
            dataset = file[f'Dataset_{i}']
        elif file_format == 'netCDF4' or file_format == 'netCDF4_compressed':
            dataset = file.variables[f'Dataset_{i}']
        else: 
            dataset = file.get(f'Dataset_{i}')
            
        # Populate datasets with the generated array of data
        if len(dimensions) == 1:
            t3 = time.perf_counter()
            dataset[:dimensions[0]] = data
        elif len(dimensions) == 2:
            t3 = time.perf_counter()
            dataset[:dimensions[0], :dimensions[1]] = data
        else:
            t3 = time.perf_counter()
            dataset[:dimensions[0], :dimensions[1], :dimensions[2]] = data
        t4 = time.perf_counter()

        # Add up the times taken to get the total time taken to create and write all datasets
        dataset_creation_time += (t2 - t1)
        dataset_population_time += (t4 - t3)


    # Zarr files can not be closed
    if (not file_format == 'Zarr') and (not file_format == 'Zarr_compressed') :
        file.close()

    # Return the average time taken to create one dataset and write to it. Times are in milliseconds
    arr = [1000 * dataset_creation_time / num_datasets, 1000 * dataset_population_time / num_datasets]
    return arr


def generate_array(num_elements):
    # Generate a random array of data with the provided dimensions
    np.random.seed(None)
    if len(num_elements) == 1:
        a = num_elements[0]
        arr = np.random.rand(a).astype(np.float32)
    elif len(num_elements) == 2:
        a, b = tuple(num_elements)
        arr = np.random.rand(a, b).astype(np.float32)
    else:
        a, b, c = tuple(num_elements)
        arr = np.random.rand(a, b, c).astype(np.float32)
    return arr
