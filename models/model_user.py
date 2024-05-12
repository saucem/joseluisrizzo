from .entities.user import User

class ModelUser():
  
  @classmethod
  def login(self, db, user):
    try:
      cur = db.connection.cursor()
      sqlSentence = "SELECT id, fullname, username, password FROM user WHERE username = '{}'".format(user.username)
      print(sqlSentence)
      cur.execute(sqlSentence)
      rowData = cur.fetchone()
      print(rowData)
      if rowData != None:
        user = User(rowData[0], rowData[2], User.check_password(rowData[3], user.password), rowData[1])
        return user
      else:
        return None
    except Exception as ex:
      raise Exception(ex)
    
  @classmethod
  def get_by_id(self, db, id):
    try:
      cur = db.connection.cursor()
      sqlSentence = "SELECT id, username, fullname FROM user WHERE id = '{}'".format(id)
      #print(sqlSentence)
      cur.execute(sqlSentence)
      rowData = cur.fetchone()
      #print(rowData)
      if rowData != None:
        logged_user = User(rowData[0], rowData[1], None, rowData[2])
        return logged_user
      else:
        return None
    except Exception as ex:
      raise Exception(ex)