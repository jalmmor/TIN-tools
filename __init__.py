# encoding: utf-8


from .tin_tools import TinTools


def classFactory(iface):
    return TinTools(iface)
