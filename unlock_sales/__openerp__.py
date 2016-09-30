# -*- coding: utf-8 -*-
{
    "name": """unlockbase phone sales""",
    "summary": """unlockbase phone sales""",
    "description": """Sales of unlock service""",
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
        "point_of_sale",
        "unlockbase",
    ],
    "external_dependencies": {'python': ['bs4']},
    "data": [
        "data/ir_action_server.xml"
    ],
    "qweb": [
    ],
    "demo": [
    ],

    'post_load' : '',
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,

}
