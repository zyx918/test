from .fds_storage_class import FDSStorageClass


class BucketBean(dict):
  """
  The FDS bucket info class.
  """

  def __init__(self, json):
    if 'name' in json.keys():
      self.bucketName = json['name']
    if 'orgId' in json.keys():
      self.orgId = json['orgId']
    if 'creationTime' in json.keys():
      self.creationTime = json['creationTime']
    if 'usedSpace' in json.keys():
      self.usedSpace = json['usedSpace']
    if 'numObjects' in json.keys():
      self.numObjects = json['numObjects']
    if 'allowOutsideAccess' in json.keys():
      self.allowOutsideAccess = json['allowOutsideAccess']
    if 'enableSSE' in json.keys():
      self.enableSSE = json['enableSSE']
    if 'storageClass' in json.keys():
      for storageClass in FDSStorageClass:
        if storageClass.name == json['storageClass']:
          self.storageClass = storageClass

  @property
  def bucketName(self):
    return self['bucketName']

  @bucketName.setter
  def bucketName(self, bucket_name):
    self['bucketName'] = bucket_name

  @property
  def orgId(self):
    return self['orgId']

  @orgId.setter
  def orgId(self, org_id):
    self['orgId'] = org_id

  @property
  def creationTime(self):
    return self['creationTime']

  @creationTime.setter
  def creationTime(self, creation_time):
    self['creationTime'] = creation_time

  @property
  def usedSpace(self):
    return self['usedSpace']

  @usedSpace.setter
  def usedSpace(self, used_space):
    self['usedSpace'] = used_space

  @property
  def numObjects(self):
    return self['numObjects']

  @numObjects.setter
  def numObjects(self, num_objects):
    self['numObjects'] = num_objects

  @property
  def allowOutsideAccess(self):
    return self['allowOutsideAccess']

  @allowOutsideAccess.setter
  def allowOutsideAccess(self, allow_outside_access):
    self['allowOutsideAccess'] = allow_outside_access

  @property
  def enableSSE(self):
    return self['enableSSE']

  @enableSSE.setter
  def enableSSE(self, enable_sse):
    self['enableSSE'] = enable_sse

  @property
  def storageClass(self):
    return self['storageClass']

  @storageClass.setter
  def storageClass(self, storage_class):
    self['storageClass'] = storage_class
