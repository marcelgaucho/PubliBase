# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsProcessingParameterVectorLayer,
                       QgsDataSourceUri)
                       
import requests
import xml.etree.ElementTree as ET

class AdvertiseStoreLayers(QgsProcessingAlgorithm):
    # Constants used to refer to parameters

    URL = 'URL'
    USER = 'USER'
    PASSWORD = 'PASSWORD'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate("Publi Base: AdvertiseStoreLayers", string) 
        
    def createInstance(self):
        return AdvertiseStoreLayers()

    def name(self):
        return 'advertise_store_layers'

    def displayName(self):
        return self.tr('Advertise Store Layers')

    def group(self):
        return 'Geoserver'

    def groupId(self):
        return 'geoserver'

    def shortHelpString(self):
        return self.tr("Advertise all the layers of a store. A featuretypes URL is needed. "
                       'An example of featuretypes URL is ' 
                       'http://localhost:8080/geoserver/rest/workspaces/cite/datastores/Publishing/featuretypes , '
                       'which targets the datastore Publishing in workspace cite.')

    def initAlgorithm(self, config=None):
        # featuretypes URL
        self.addParameter(QgsProcessingParameterString(
            self.URL,
            "URL"))

        # Geoserver user            
        self.addParameter(QgsProcessingParameterString(
            self.USER,
            self.tr("User"),
            "admin"))    

        # Geoserver password
        self.addParameter(QgsProcessingParameterString(
            self.PASSWORD,
            self.tr("Password"),
            "geoserver"))

    def processAlgorithm(self, parameters, context, feedback):
        """
        Retrieving parameters
        an URL example is 'http://localhost:8080/geoserver/rest/workspaces/cite/datastores/Publicacao/featuretypes'
        """
        url = parameters[self.URL]
        headers = {'Content-type': 'text/xml'}
        user = parameters[self.USER]
        password = parameters[self.PASSWORD]

        # Debugging info
        feedback.pushInfo('Input variables')
        feedback.pushInfo('url = ' + url)
        feedback.pushInfo('user = ' + user)
        feedback.pushInfo('password = ' + password)
        feedback.pushInfo('')
        
        # Get layers in the datastore 
        headers = {'Accept': 'application/xml'}
        resp = requests.get(url, auth=(user,password), headers=headers)
        resp.raise_for_status() # raise error depending on the result
        xml = resp.text
        feedback.pushInfo('xml featuretypes')
        feedback.pushInfo(xml)
        feedback.pushInfo('')
        
        # Store featuretypes name parsing xml to Python
        featuretypes = []
        root = ET.fromstring(xml)
        for element in root:
            name_element = element.find('name')
            name = name_element.text
            featuretypes.append(name)
                
        feedback.pushInfo('FeatureTypes Names')                
        feedback.pushInfo(str(featuretypes_name))
        feedback.pushInfo('')
        
        # Store payloads in list      
        payloads = []
        for name in featuretypes:
            a = ("""<featureType>
                    <name>""" + name + """</name>
                    <advertised>true</advertised>
                    </featureType>""")
            payloads.append(a)
            
        feedback.pushInfo('payloads = ' + str(payloads))
        feedback.pushInfo('')
        
        # Advertising
        headers = {'Content-type': 'text/xml'}
        for i, payload in enumerate(payloads):
            resp = requests.put(url + '/' + featuretypes[i], auth=(user, password), data=payload, headers=headers)
            feedback.pushInfo("Advertised layer was " + featuretypes[i])
            feedback.pushInfo('server response for above layer was = ' + resp.text)
            
        return {'Result': 'Layers advertised'}
