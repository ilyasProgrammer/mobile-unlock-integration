# -*- coding: utf-8 -*-
{
    "name": """Product prices management""",
    "summary": """Product prices management""",
    "description": """Set prices for custom products groups""",
    "category": "Sales",
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
        "product",
    ],
    "external_dependencies": {},
    "data": [
        'wizard.xml',
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
