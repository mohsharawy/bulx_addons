# Copyright 2015-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2017 Ilmir Karamov <https://it-projects.info/team/ilmir-k>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2018 Ildar Nasyrov <https://it-projects.info/team/iledarn>
# Copyright 2018 WohthaN <https://github.com/WohthaN>
# Copyright 2019 Eugene Molotov <https://github.com/em230418>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': "Backend debranding",
    'version': '12.0.1.0.28',
    'author': 'Classera',
    'license': 'LGPL-3',
    'category': 'Debranding',
    'images': ['images/web_debranding.png'],
    'website': 'https://twitter.com/yelizariev',

    'depends': [
        'web',
        'mail',
        'access_settings_menu',
    ],
    'data': [
        'data.xml',
        'views.xml',
        'js.xml',
        'pre_install.xml',
    ],
    'qweb': [
        'static/src/xml/web.xml',
    ],
    "post_load": 'post_load',
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'saas_demo_title': 'Backend debranding demo',
}
