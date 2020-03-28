# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html





class OuvPipeline(object):
    def process_item(self, item, spider):
        return item
import psycopg2


class ParaPostgres(object):

    def open_spider(self, spider):
        hostname = 'localhost'
        username = 'postgres'
        password = 'base44'
        database = 'observatoriogott'
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()

    def process_item(self, item, spider):
        self.cur.execute("insert into base1(codigo,url,siteorigem,data,tipologia,titulo,preco,condominio,area,anunciante,telefone,descricao,caracteristica,quarto,suite,banheiro,vaga,andar,endereco,bairro,municipio,uf,urlmapa,imagem,imagemlista,latitude,longitude) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(item['codigo'],item['url'],item['siteorigem'],item['data'],item['tipologia'],item['titulo'],item['preco'],item['condominio'],item['area'],item['anunciante'],item['telefone'],item['descricao'],item['caracteristica'],item['quarto'],item['suite'],item['banheiro'],item['vaga'],item['andar'],item['endereco'],item['bairro'],item['municipio'],item['uf'],item['url'],item['imagem'],item['imagemlista'],item['latitude'],item['longitude']))
        self.connection.commit()
        return item

# datetime.datetime.now()] #comando para inserir datatime. Parâmetros: data, %s, item['datetime.datetime.now()']
