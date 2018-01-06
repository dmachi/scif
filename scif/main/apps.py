'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

from scif.logger import bot
from scif.main.helpers import parse_entrypoint
from scif.defaults import SCIF_ENTRYFOLDER
import sys
import os


def app(self, app):
    '''view a single app, if it exists

    Parameters
    ==========
    app: the name of the app to view
        '''
    if 'apps' in self._config:
        if app in self._config['apps']:
            return self._config['apps'][app]

def apps(self):
    '''get a list of apps to show the user
    '''
    apps = []
    if self._config is not None:
        if "apps" in self._config:
            apps = list(self._config['apps'])
    return apps


def activate(self, app, cmd=None):
    '''if an app is valid, get it's environment to make it active.
       Update the entrypoint to be relevant to the app runscript.
    
    Parameters
    ==========
    app: the name of the app to activate
    cmd: if defined, the entry point (command) to run. Otherwise uses apprun
    '''
    if app is None:
        bot.warning('No app selected, will run default %s' %self._entry_point)    
        self.reset()

    elif app in self.apps():
        config = self.app(app)

        # Make app active
        self._active = app

        # Set the entry point
        if cmd is not None:
            self._entry_point = parse_entrypoint(cmd)
        
        elif 'apprun' in config:   
            self._entry_point = parse_entrypoint(config['apprun'])
 
        # Update the environment for active app (updates ScifRecipe object)
        appenv = self.get_appenv(app, isolated=False, update=True)

        # We also want to load the environment script for running, if it exists
        self.load_env(app)

        # Only set entryfolder if user didn't set to something else
        if not SCIF_ENTRYFOLDER:
            self._entry_folder = appenv['SCIF_APPROOT']

    else:        
        bot.warning('%s is not an installed SCIF app' %app)


def deactivate(self, app):
    '''if an app is valid, change the state so the app is no longer active.
       This is currently equivalent to calling reset, but only doing so if the
       app is defined for the SCIF.

    Parameters
    ==========
    app: the name of the app to deactivate
    '''

    if app in self.apps():
        self.reset()

    else:        
        bot.warning('%s is not an installed SCIF app' %app)


def reset(self):
    '''reset the SCIF filesystem, meaning that defaults are set, the entrypoint
      if reset, and the environment is reset. Only maintain entry folder set
      by environment, if it was defined.
    '''

    self.set_defaults()
    # Make the active app None
    # self._active = None
    # Update the entry point to use default
    # self._entry_point = parse_entrypoint()
 
    # Reset the environment
    self.update_env(reset=True)

    # set entry folder back to use preference, if original is not None
    if not SCIF_ENTRYFOLDER:
        self._entry_folder = SCIF_ENTRYFOLDER        


def inspect(self, app, attributes):
    '''inspect an app based on a list of attributes to inspect.

    Parameters
    ==========
    app: the name of the app to inspect
    attributes: a list of attributes to return
    '''
    result = {}
    if app not in self.apps():
        return result

    lookup = self.app(app)

    if 'a' in attributes or 'all' in attributes:
        return lookup

    if 'f' in attributes or 'files' in attributes and 'appfiles' in lookup:
        result['appfiles'] = lookup['appfiles']
    if 'r' in attributes or 'runscript' in attributes and 'apprun' in lookup:
        result['apprun'] = lookup['apprun']
    if 'l' in attributes or 'labels' in attributes and 'applabels' in lookup:
        result['applabels'] = lookup['applabels']
    if 'e' in attributes or 'environment' in attributes and 'appenv' in lookup:
        result['appenv'] = lookup['appenv']
    if 'i' in attributes or 'install' in attributes and 'appinstall' in lookup:
        result['appinstall'] = lookup['appinstall']
    return result
