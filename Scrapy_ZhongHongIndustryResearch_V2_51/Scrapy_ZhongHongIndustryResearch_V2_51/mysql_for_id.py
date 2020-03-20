import pymysql
import logging


class OperateMysql(object):
    def __init__(self, db_name='industry_data', table_name='wood_report_copy1'):
        self.db = pymysql.Connect(host='127.0.0.1', user='root',  password='123456', db=db_name)
        self.cursor = self.db.cursor()
        self.table_name = table_name

    def insert_id(self, name, in_pid):
        """
        根据name，在mysql中查找，

        若有，则返回这个已存在mysql的目录的id
        若没有，就自己生成一个
        生成规则：
            有in_pid则在该id下生成（in_pid是该目录的上级目录的ID）
            ### 在上级目录的id下依次查找XXX001， XXX002、、、直到找到一个不存在于mysql的id就把它作为这个目录的id存进mysql并且返回此id给爬虫

        :parameter: 目录的name和pid
        :returns: 得到的id
        """

        # 查询mysql中是否存在该目录, 数据全部查询出来
        find_sql = 'select dir_name, id from {};'.format(self.table_name)
        self.cursor.execute(find_sql)
        find_results = self.cursor.fetchall()
        pid = 0
        for result in find_results:
            if name == result[0]:
                pid = result[1]
                break
        # mysql中存在该目录，直接返回pid
        if pid:
            return pid
        # mysql中不存在该目录，自己生成一个并返回
        else:
            pid = in_pid
            num = 1
            find_results = set(i[1] for i in find_results)
            while True:
                # 如果该目录下子目录超出999条，则往后推一个pid（因为目前没有遇到过，所以暂时这样处理）
                if num > 999:
                    sql_get_name = 'select dir_name from {} where id={};'.format(self.table_name, pid)
                    self.cursor.execute(sql_get_name)
                    pname = self.cursor.fetchone()[0]
                    pid = int(pid) + 1
                    sql_get_name = 'select dir_name from {} where id={};'.format(self.table_name, pid)
                    self.cursor.execute(sql_get_name)
                    pname2 = self.cursor.fetchone()
                    if not pname2:
                        pname2 = pname + '1'
                        self._insert_catalogue(pname2, pid)
                    num = 1
                else:
                    find_id = str(pid) + '0' * (3 - len(str(num))) + str(num)
                    if find_id in find_results:
                        num += 1
                    else:
                        self._insert_catalogue(name=name, pid=find_id)
                        break
            return find_id

    def _insert_catalogue(self, name, pid):
        id = str(pid)
        dir_name = name
        root_id = str(pid)[:2]
        parent_id = id[:-3]
        has_parent = 1
        has_children = 0
        sort_num = sort_flag = 0
        level = (len(id) - 1) / 3
        sql = "insert into {} values ({},{},{},{},{},{},{},{},{});".format(self.table_name, repr(id), repr(dir_name),
                                                                           repr(root_id), repr(parent_id),
                                                                           repr(has_parent), repr(has_children),
                                                                           repr(sort_num), repr(sort_flag),
                                                                           repr(level))
        # 插入目录
        try:
            self.cursor.execute(sql)
            self.db.commit()
            # logger.info('插入目录成功')
        except Exception as e:
            logging.error(e.args, end='  ')
            logging.error("Error: unable to insert data")
            self.db.rollback()

    def close(self):
        self.cursor.close()
        self.db.close()


if __name__ == '__main__':
    op_mysql = OperateMysql()
    in_id = op_mysql.insert_id('一条目录', 3008003)
    print(in_id)

    op_mysql.close()

