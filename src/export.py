import data
import logging
import nibabel as nib
import os
import progress.bar 
import scipy.misc
import scipy.misc.pilutil as pilutil

def export_all(subjects, folder):
  assert(folder[:1] == '/')
  logging.info('Exporting subjects...')
  suffix_format ='%(index)d/%(max)d [%(elapsed_td)s / %(eta_td)s]'
  bar = progress.bar.Bar('Exporting subjects', max=len(subjects), suffix=suffix_format)
  for subject in subjects:
    export_subject(subject, folder)
    bar.next()
  bar.finish()

def export_subject(subject, folder):
  logging.debug(f'Exporting subject {subject.subject_id}')
  for mri_data in subject.mri_data:
    for i, filename in enumerate(mri_data.filenames):
      path =  folder + f'{subject.subject_id}_{i}.png'
      if not os.path.isfile(path):
        img = load_image(filename + '.nii.gz')
        pilutil.imsave(path, get_single_plane(img))
        

def get_planes(img):
  a, b, c = img.shape
  slice1 = img.dataobj[a // 2, :, :]
  slice2 = img.dataobj[:, b // 2, :]
  slice3 = img.dataobj[:, :, c // 2]
  return slice1, slice2, slice3

def get_single_plane(img):
  a, b, c = img.shape
  size = min(a, b)
  a_min, a_max = get_center_dims(a, size)
  b_min, b_max = get_center_dims(b, size)
  return img.dataobj[a_min:a_max, b_min:b_max, c // 2]

def get_center_dims(org_size, size):
  margin = (org_size-size) // 2
  return margin, org_size - margin

def save_planes(subject, index, planes, folder):
    suffixes = 'abc'
    for i, plane in enumerate(planes):
      path =  folder + f'{subject.subject_id}{index}{suffixes[i]}.png'
      if not os.path.isfile(path):
        pilutil.imsave(path, plane)


def load_image(path):
  # Reorient image so the axes become RAS-oriented
  return nib.as_closest_canonical(nib.load(path))
