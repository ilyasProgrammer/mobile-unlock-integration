<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>UnlockBase API : Examples : GetToolNetworks</title>
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
        <h1>GetToolNetworks</h1>
        <?php
        /* Include the library */
        require('../Library/API.php');

        /*
         * First, let's search for a tool that needs the mobile phone carrier
         * ==================================================================
         */

        $Found = false;

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
                    foreach ($Data['Group'] as $Group) {
                        foreach ($Group['Tool'] as $Tool) {
                            if ($Tool['Requires.Network'] != 'None') {
                                /* We found a candidate for GetToolNetworks */
                                $Found = true;
                                break 2;
                            }
                        }
                    }
                }
            } else {
                /* Parsing error */
                print('Could not parse the XML stream');
            }
        } else {
            /* Communication error */
            print('Could not communicate with the api');
        }

        /*
         * Now, let's call GetToolNetworks for this tool
         * ============================================
         */

        if ($Found) {
            print('<p>List of the mobile phone carriers supported by the tool <b>' . htmlspecialchars($Tool['Name']) . '</b></p>');

            /* Call the API */
            $XML = UnlockBase::CallAPI('GetToolNetworks', array('ID' => $Tool['ID']));

            if (is_string($XML)) {
                /* Parse the XML stream */
                $Data = UnlockBase::ParseXML($XML);

                if (is_array($Data)) {
                    if (isset($Data['Error'])) {
                        /* The API has returned an error */
                        print('API error : ' . htmlspecialchars($Data['Error']));
                    } else {
                        /* Everything works fine */
                        foreach ($Data['Network'] as $Network) {
                            print(htmlspecialchars($Network['Name']));
                            print('<br />');
                        }
                    }
                } else {
                    /* Parsing error */
                    print('Could not parse the XML stream');
                }
            } else {
                /* Communication error */
                print('Could not communicate with the api');
            }
        }
        ?>
        <p><a href="./">Go back</a></p>
    </body>
</html>