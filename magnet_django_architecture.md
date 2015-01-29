#Magnet Django Architecture

Since Magnet is built on top of the Django framework, the source code is organized as follows:

- Core: the Magnet Engine
- Web: the Web Module, provides fucntions/methods to present Magnet as a Web site
- Magnet: the master app, provides links between Core and Web and collects various settings.
- manage.py: a Python file which runs commands, as the development server

Along with the Magnet Django-based app, there is the *schema.dtd* file, which provides the schema for the response returned from /classify or /rest/classify query.