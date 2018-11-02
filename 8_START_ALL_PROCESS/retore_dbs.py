# -*- coding: utf-8 -*-
import socket, time, sys, os, thread, platform
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from datetime import datetime

 
class Restore_Databases:
   
    def __init__(self, config, logger=False):
        self.logger = logger
        self.user_data = config
        self.exported_db_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), '8_START_ALL_PROCESS', 'exported_bkp')
        self.psql_path = u'export PGPASSWORD="{0}"; psql'.format(self.user_data['database_user_password']) 
        self.logger.debug(u"PSQL_PATH : {0} user : {1}".format(self.psql_path, self.user_data['branch_name']))
        self.os = os
        self.backup_path = None

    def create_dir(self, path):
        if not(os.path.exists(path)):
            os.mkdir(path)
    
    def restore_exported_db(self):
        self.logger.info(
            u"Backup database: {0}, user : {1}".format(
                self.user_data['database_name'], 
                self.user_data['branch_name']
            )
        )
        self.backup_path = u"{0}.sql".format(os.path.join(
                self.exported_db_path,
                'exported_db'   
            )
        )
        cmd = u'{psql} -U {name} -h {m_ip} -p {m_port} -d {db_name} -f {bkp_path}'.format(
            name = self.user_data['database_user_name'],
            m_ip = self.user_data['machine_ip'],
            m_port = self.user_data['machine_port'],
            db_name = self.user_data['database_name'],
            bkp_path = self.backup_path,
            psql=self.psql_path
        )
        self.logger.debug(u"Backup database cmd : {0} - user : {1}".format(cmd, self.user_data['branch_name']))
        self.os.popen(cmd)
        return os.path.exists(self.backup_path)
    
    def drop_create_db(self):
        self.logger.info(
            u"Drop/Create database: {0}, user : {1}".format(
                self.user_data['database_name'], 
                self.user_data['branch_name']
            )
        )
        query = u'''SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{0}'
        AND pid <> pg_backend_pid();\ndrop database {0};\ncreate database {0};'''.format(dbname)
        cmd = u'''{psql} -U {name} -h {m_ip} -p {m_port} -d {db_name} << EOF\n{query}\nEOF'''.format(
            name = self.user_data['database_user_name'],
            m_ip = self.user_data['machine_ip'],
            m_port = self.user_data['machine_port'],
            db_name = self.user_data['database_name'],
            query = query,
            psql=self.psql_path
        )
        self.logger.debug(u"Drop/Create database cmd : {0} - user : {1}".format(cmd, self.user_data['branch_name']))
        self.os.popen(cmd)
        return os.path.exists(self.backup_path)
      
    def run_process(self):
        self.logger.info(u"Drop/Create/Restore - user  : {0}".format(self.user_data['branch_name']))
        self.drop_create_db()
        self.restore_exported_db()
        
if __name__ == '__main__':
    n = sys.argv[1]
    branch = sys.argv[2]
    date = sys.argv[3]
    USER = USERS.ALL_CONFIG[int(n)]
    logger, log_path = logger.get_low_logger(date, branch, 'restore_all_dbs_users')
    try:
        if not connection.check(USER, logger):
            raise Exception(u'Erro conexão')
        process = Pull_Export(USER, logger)
        result = process.run_process()
        if result:
            logger.info(u"Pull e Export finalizado sem erros")
        else:
            logger.error(u"Erro no processo de Pull/Export")
    except Exception as e:
        logger.error(e)
    finally:
        pass
        #smtp.send_email_with_attach(u"desenv.1dl@gmail.com", u"desenv1dl", [u"desenv.1dl@gmail.com", "diniz.ime@gmail.com","cesar.soares@gmail.com"], 'Pull_Export', log_path)
