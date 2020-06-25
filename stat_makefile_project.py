#!/usr/bin/env python

# SPDX-FileCopyrightText: (c) 2020 Western Digital Corporation or its affiliates,
#                             Arseniy Aharonov <arseniy@aharonov.icu>
#
# SPDX-License-Identifier: MIT

import os

import stat_attributes as attributes
from directory_tree_node import DirectoryTreeNode
from stat_makefile import StatMakefile
from itertools import chain

class StatMakefileProject(object):
    """
    Constructs a STAT project built based on STAT makefile
    """

    def __init__(self, fileName):
        self.__fileName = fileName
        self.__makefile = StatMakefile(fileName)
        self.__tree = None
        self.__sources = None
        self.__headers = None
        self.__headerNames = []

    @property
    def makeFile(self):
        return self.__fileName

    @property
    def projectName(self):
        return self.__makefile.name

    @property
    def outputName(self):
        return self.__makefile[StatMakefile.NAME]

    @property
    def tree(self):
        if self.__tree is None:
            self.__tree = self.__buildFileTree()
        return self.__tree

    @property
    def sources(self):
        """
        @rtype: DirectoryTreeNode
        """
        if self.__sources is None:
            self.__buildSourcesDirectoryTree()
        return self.__sources

    @property
    def headers(self):
        """
        @rtype: DirectoryTreeNode
        """
        if self.__headers is None:
            self.__buildHeadersDirectoryTree()
        return self.__headers

    @property
    def definitions(self):
        return self.__makefile[StatMakefile.DEFINES].split()

    def files(self):
        return chain(self.__sourceFiles(), self.__headerFiles())

    def __getitem__(self, key):
        return self.__makefile[key]

    def __iter__(self):
        return iter(self.__makefile)

    def __buildFileTree(self):
        tree = DirectoryTreeNode()
        for _file in self.files():
            tree.addFile(_file)
        return tree

    def __sourceFiles(self):
        for source in self.__makefile[StatMakefile.SOURCES].split():
            yield source

    def __headerFiles(self):
        files = []
        for file in self.__makefile[StatMakefile.INTERFACES].split():
            filePath = os.path.join(attributes.DUMMIES_DIRECTORY, file)
            files.append(os.path.basename(filePath))
            yield filePath
        for pathName in self.__makefile[StatMakefile.INCLUDES].split():
            for file in os.listdir(pathName):
                if file.endswith('.h') and file not in files:
                    files.append(file)
                    yield os.path.join(pathName, file)

    def __buildSourcesDirectoryTree(self):
        self.__sources = DirectoryTreeNode()
        for source in self.__makefile[StatMakefile.SOURCES].split():
            self.__sources.addFile(source)

    def __buildHeadersDirectoryTree(self):
        self.__headers = DirectoryTreeNode()
        self.__addDummyHeaderFiles()
        self.__addHeaderFilesFromIncludePaths()

    def __addDummyHeaderFiles(self):
        for header in self.__makefile[StatMakefile.INTERFACES].split():
            self.__addHeaderFile(header, attributes.DUMMIES_DIRECTORY)

    def __addHeaderFilesFromIncludePaths(self):
        for pathName in self.__makefile[StatMakefile.INCLUDES].split():
            for header in [fileName for fileName in os.listdir(pathName) if fileName.endswith('.h')]:
                self.__addHeaderFile(header, pathName)

    def __addHeaderFile(self, fileName, pathName):
        if fileName not in self.__headerNames:
            self.__headerNames.append(fileName)
            self.__headers.addFile(os.path.join(pathName, fileName))
