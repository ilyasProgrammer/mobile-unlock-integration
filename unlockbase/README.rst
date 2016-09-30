============
 unlockbase
============

How it works:

 * Module depends on gsmarena database.
 * It gets datad from unlockbase.com
 * Looking for mobile brands in odoo database (product.category).
     * If category exists it adds brand id and other data to it.
     * If category absent, it creates new category under 'unbound brands' category.
 * Assumes that most of brands must to exist before gsmarena data load.
 * Next it looking for mobiles in odoo database (product.product).
     * If mobile exists it adds unlock data to it.
         * Also it creates new category with that mobile name.
         * In this category it add 'unlock tools' products, according to received data.
     * If mobile absent, it creates new mobile under 'unbound mobiles' category.