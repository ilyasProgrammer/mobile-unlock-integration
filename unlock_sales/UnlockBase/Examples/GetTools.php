<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>UnlockBase API : Examples : GetTools</title>
        <style type="text/css">
            <!--
            body, td {
                font-family: Arial;
                font-size: 11px;
                color: #333333;
                white-space: nowrap;
            }

            td {
                border-width: 0px 0px 1px 1px;
                border-style: dotted;
                border-color: #DDDDDD;
                padding: 2px;
            }

            h1 {
                font-size: 16px;
            }

            a {
                color: #6699CC;
            }

            a:hover {
                text-decoration: none;
            }
            -->
        </style>
    </head>

    <body>
        <h1>GetTools</h1>
        <?php
        /* Include the library */
        require('../Library/API.php');

        /* Call the API */
        $XML = UnlockBase::CallAPI('GetTools');

        if (is_string($XML)) {
            /* Parse the XML stream */
            $Data = UnlockBase::ParseXML($XML);

            if (is_array($Data)) {
                if (isset($Data['Error'])) {
                    /* The API has returned an error */
                    print('API error : ' . htmlspecialchars($Data['Error']));
                } else {
                    /* Everything works fine */
                    print('<table>');

                    foreach ($Data['Group'] as $Group) {
                        print('<tr>');
                        print('<td><b>' . htmlspecialchars($Group['Name']) . '</b></td>');
                        foreach ($Group['Tool'] as $Tool) {
                            print('<td>' . htmlspecialchars($Tool['Name']) . '<br /><b>' . htmlspecialchars($Tool['Credits']) . ' credits</b></td>');
                        }
                        print('</tr>');
                    }

                    print('</table>');
                }
            } else {
                /* Parsing error */
                print('Could not parse the XML stream');
            }
        } else {
            /* Communication error */
            print('Could not communicate with the api');
        }
        ?>
        <p><a href="./">Go back</a></p>
    </body>
</html>