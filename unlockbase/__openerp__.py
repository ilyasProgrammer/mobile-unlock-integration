# -*- coding: utf-8 -*-
{
    "name": """unlockbase data load""",
    "summary": """Load mobiles data form unlockbase.com""",
    "description": """Load mobiles data form unlockbase.com""",
    "category": "Web",
    "images": [],
    "version": "1.0.0",

    "author": "Ilyas",
    "website": "",
    "license": "GPL-3",
    #"price": 9.00,
    #"currency": "EUR",

    "depends": [
        "base",
        "web",
        "gsmarena",
    ],
    "external_dependencies": {'python': ['bs4']},
    "data": [
        "data/cron.xml",
        "data/ir_config_parameter.xml",
    ],
    "qweb": [
    ],
    "demo": [
    ],

    'post_load': '',
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,

}
