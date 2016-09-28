<?php
	/*
                      _/    _/            _/                      _/        _/_/_/
                     _/    _/  _/_/_/    _/    _/_/      _/_/_/  _/  _/    _/    _/    _/_/_/    _/_/_/    _/_/
                    _/    _/  _/    _/  _/  _/    _/  _/        _/_/      _/_/_/    _/    _/  _/_/      _/_/_/_/
                   _/    _/  _/    _/  _/  _/    _/  _/        _/  _/    _/    _/  _/    _/      _/_/  _/
                    _/_/    _/    _/  _/    _/_/      _/_/_/  _/    _/  _/_/_/      _/_/_/  _/_/_/      _/_/_/


                                                           
                                    _|_|     _|_|_|     _|_|_|                    _|_|_|    
                                  _|    _|   _|    _|     _|         _|      _|         _|  
                                  _|_|_|_|   _|_|_|       _|         _|      _|     _|_|    
                                  _|    _|   _|           _|           _|  _|           _|  
                                  _|    _|   _|         _|_|_|           _|       _|_|_|    
                                                           
                                                           

		This is a PHP 4/5 library for connecting the UnlockBase API (v3)

		It supposes that you have cURL installed.
		If it is not the case, please ask your system administrator.
		More information : http://www.php.net/curl

		If you need assistance, please contact tech@unlockbase.com
	*/

	/* Enter your API key here */

	define('UNLOCKBASE_API_KEY', '(XXXX-XXXX-XXXX-XXXX)');
	
	/* Set this value to true if something goes wrong and you want to display error messages */
	
	define('UNLOCKBASE_API_DEBUG', false);
	
	/* This is the url of the api, don't change it */

	define('UNLOCKBASE_API_URL', 'http://www.unlockbase.com/xml/api/v3');
	
	/*
		To allow UnlockBase class functions to be called statically - e.g. UnlockBase::Function()
		and to keep backward compatibility with PHP4, some variables to be shared between
		member functions will be allocated globally. Their names are listed below.
		This is just for information, as they almost certainly won't interact in any way with your scripts.
		If you did not understand the above, this is not important :-)
		
		For the same reason (backward compatibility), you may experience warnings such as :
		Strict standards : Non-static method UnlockBase:: ... () should not be called statically
		In this case, change your error reporting directive to remove the E_STRICT level,
		Or, if this is not acceptable to you, add a static keyword in front of each function name in this file.
	*/
	
	define('UNLOCKBASE_VARIABLE_ERROR',    '_UnlockBaseError'    );
	define('UNLOCKBASE_VARIABLE_ARRAY',    '_UnlockBaseArray'    );
	define('UNLOCKBASE_VARIABLE_POINTERS', '_UnlockBasePointers' );
	
	/* Check that cURL is installed */
	
	if (! extension_loaded('curl'))
	{
		trigger_error('cURL extension not installed', E_USER_ERROR);
	}
	
	/* Here comes the main class */
	
	class UnlockBase
	{
		/*
			mixed UnlockBase::CallAPI (string $Action, array $Parameters)
			Call the UnlockBase API.
			Returns the xml stream sent by the UnlockBase server
			Or false if an error occurs
		*/

		public static function CallAPI ( $Action, $Parameters = array() )
		{
			if (is_string($Action))
			{
				if (is_array($Parameters))
				{
					/* Add the API Key and the Action to the parameters */
					$Parameters['Key'] = UNLOCKBASE_API_KEY;
					$Parameters['Action'] = $Action;

					/* Prepare the cURL session */
					$Ch = curl_init(UNLOCKBASE_API_URL);		
					curl_setopt($Ch, CURLOPT_CONNECTTIMEOUT, 10);
					curl_setopt($Ch, CURLOPT_TIMEOUT, 30);
					curl_setopt($Ch, CURLOPT_HEADER, false);
					curl_setopt($Ch, CURLOPT_RETURNTRANSFER, true);
					curl_setopt($Ch, CURLOPT_ENCODING, '');
					curl_setopt($Ch, CURLOPT_POST, true);
					curl_setopt($Ch, CURLOPT_POSTFIELDS, UnlockBase::BuildQuery($Parameters));
					
					/* Perform the session */
					$Data = curl_exec($Ch);
					
					if (UNLOCKBASE_API_DEBUG && curl_errno($Ch) != CURLE_OK)
					{
						/* If an error occurred, report it in debug mode */
						trigger_error(curl_error($Ch), E_USER_WARNING);
					}
					
					/* Close the session */
					curl_close($Ch);
					
					/* Return the data, or false if an error occurred */
					return $Data;
				}
				else trigger_error('Parameters must be an array', E_USER_WARNING);
			}
			else trigger_error('Action must be a string', E_USER_WARNING);
			
			return false;
		}

		/*
			mixed UnlockBase::ParseXML (string $XML)
			Parse an XML stream from the UnlockBase API.
			Returns an associative array of the parsed XML string
			Or false if an error occurs
		*/
		
		public static function ParseXML ( $XML )
		{
			if (! is_string($XML))
			{
				/* If the argument is not a string, report the error in debug mode & stop here */
				if (UNLOCKBASE_API_DEBUG) trigger_error('Invalid argument supplied for UnlockBase::ParseXML()', E_USER_WARNING);
				return false;
			}

			/* Globalize variables */
			global ${UNLOCKBASE_VARIABLE_ERROR}    ;
			global ${UNLOCKBASE_VARIABLE_ARRAY}    ;
			global ${UNLOCKBASE_VARIABLE_POINTERS} ;

			/* Initialize variables */
			${UNLOCKBASE_VARIABLE_ERROR}    = false   ;
			${UNLOCKBASE_VARIABLE_ARRAY}    = array() ;
			${UNLOCKBASE_VARIABLE_POINTERS} = array() ;

			/* Configure the parser */
			$Parser = xml_parser_create('UTF-8');
			xml_set_element_handler($Parser, array('UnlockBase', 'XML_Start'), array('UnlockBase', 'XML_End'));
			xml_set_character_data_handler($Parser, array('UnlockBase', 'XML_CData'));
			xml_parser_set_option($Parser, XML_OPTION_CASE_FOLDING, 0);
			
			/* Start parsing, check the success of both parsing and analyzing */
			$Success = xml_parse($Parser, $XML, true) && ! ${UNLOCKBASE_VARIABLE_ERROR};
			
			/* Report errors in debug mode */
			if (UNLOCKBASE_API_DEBUG)
			{
				if (${UNLOCKBASE_VARIABLE_ERROR})
				{
					/* The XML stream has not been recognized */
					trigger_error('Unrecognized XML format', E_USER_WARNING);
				}
				elseif (xml_get_error_code($Parser) != XML_ERROR_NONE)
				{
					/* A parser error occurred */
					trigger_error(xml_error_string(xml_get_error_code($Parser)), E_USER_WARNING);
				}
			}

			/* Free the parser */
			xml_parser_free($Parser);
			
			/* Get a reference to the result */
			$Array =& ${UNLOCKBASE_VARIABLE_ARRAY};
			
			/* Unset global variables */
			unset ( $GLOBALS[UNLOCKBASE_VARIABLE_ERROR]    );
			unset ( $GLOBALS[UNLOCKBASE_VARIABLE_ARRAY]    );
			unset ( $GLOBALS[UNLOCKBASE_VARIABLE_POINTERS] );

			/* Return the result */
			return ($Success ? $Array : false);
		}

		/*
			bool UnlockBase::CheckEmail (string $Email)
			Check the validity of an email address
			This function is *not* RFC 2822 compliant, but instead reflects today's email reality
			Returns true if the email address seems correct, false otherwise
		*/
		
		public static function CheckEmail ( $Email )
		{
			return (bool) preg_match('/^[0-9a-z_\\-\\.]+@([0-9a-z][0-9a-z\\-]*[0-9a-z]\\.)+[a-z]{2,}$/i', $Email);
		}

		/*
			bool UnlockBase::CheckIMEI (string $IMEI, bool $Checksum)
			Check a 15-digit IMEI serial number.
			You are free to verify the checksum, or not;
			Bad checksums are 99% likely to provide unavailable unlock codes (exceptions exist, however)
			Returns true if the IMEI seems correct, false otherwise
		*/
		
		public static function CheckIMEI ( $IMEI, $Checksum = true )
		{
			if (is_string($IMEI))
			{
				if (ereg('^[0-9]{15}$', $IMEI))
				{
					if (! $Checksum) return true;

					for ($i = 0, $Sum = 0; $i < 14; $i++)
					{
						$Tmp = $IMEI[$i] * ( ($i % 2) + 1 );
						$Sum += ($Tmp % 10) + intval($Tmp / 10);
					}
					
					return ( ( ( 10 - ( $Sum % 10 ) ) % 10 ) == $IMEI[14] );
				}
			}
			
			return false;
		}
		
		/*
			bool UnlockBase::CheckProviderID (string $ProviderID)
			Verify an Alcatel Provider ID
			Returns true if the Provider ID seems correct, false otherwise
		*/
		
		public static function CheckProviderID ( $ProviderID )
		{
			return (is_string($ProviderID) && eregi('^[0-9a-z]{4,5}\\-[0-9a-z]{7}$', $ProviderID));
		}
		
		/*
			bool UnlockBase::CheckMEP_PRD (string $Type, string $String)
			Check a MEP/PRD number before submitting it to the API
			$Type is either 'MEP' or 'PRD'
			Returns true if the MEP/PRD seems correct, false otherwise
		*/
		
		public static function CheckMEP_PRD( $Type, $String )
		{
			return ereg('^' . $Type . '\\-[0-9]{5}\\-[0-9]{3}$', $String);
		}
	
		/* Internal functions - do not care */
		
		static function BuildQuery ( $Parameters )
		{
			if (function_exists('http_build_query'))
			{ 
				/* PHP 5 */
				return http_build_query($Parameters);
			}
			else
			{
				/* PHP 4 */
				$Data = array();
				foreach ($Parameters as $Name => $Value) array_push($Data, urlencode($Name) . '=' . urlencode($Value));
				return implode('&', $Data);
			}
		}

		static function XML_Start ( $Parser, $Name, $Attributes )
		{
			/* Globalize variables */
			global ${UNLOCKBASE_VARIABLE_ERROR};
			global ${UNLOCKBASE_VARIABLE_ARRAY};
			global ${UNLOCKBASE_VARIABLE_POINTERS};
			
			/* Do nothing if an error occurred previously */
			if (${UNLOCKBASE_VARIABLE_ERROR}) return;

			if (count( ${UNLOCKBASE_VARIABLE_POINTERS} ) == 0)
			{
				/* Root Element : create the first pointer to the array */
				${UNLOCKBASE_VARIABLE_POINTERS}[] =& ${UNLOCKBASE_VARIABLE_ARRAY};
			}
			else
			{
				/* Get the latest pointer */
				$Pointer =& ${UNLOCKBASE_VARIABLE_POINTERS} [ count( ${UNLOCKBASE_VARIABLE_POINTERS} ) -1 ];
				
				if (is_null($Pointer))
				{
					/* This is the first sub-tag with that name, create the new container array for it */
					$Pointer[] = array();
					
					/* Replace the latest pointer, point to the first item of the new container */
					${UNLOCKBASE_VARIABLE_POINTERS}[ count(${UNLOCKBASE_VARIABLE_POINTERS}) -1 ] =& $Pointer[0];
					$Pointer =& $Pointer[0];
				}
				elseif (is_array($Pointer))
				{
					if (isset($Pointer[$Name]))
					{
						if (! is_array($Pointer[$Name]))
						{
							/* Unrecognized XML stream */
							${UNLOCKBASE_VARIABLE_ERROR} = true;
							return;
						}
						
						/* The tag is already known, add an item to the array and create a pointer to it */
						$Pointer[$Name][] = array();
						${UNLOCKBASE_VARIABLE_POINTERS}[] =& $Pointer[$Name][ count($Pointer[$Name]) -1 ];
						return;
					}
				}
				else
				{
					/* Unrecognized XML stream */
					${UNLOCKBASE_VARIABLE_ERROR} = true;
					return;
				}
				
				/* Set the default value and create a pointer to it */
				$Pointer[$Name] = NULL;
				${UNLOCKBASE_VARIABLE_POINTERS}[] =& $Pointer[$Name];
			}
		}
		
		static function XML_End ( $Parser, $Name )
		{
			/* Globalize variables */
			global ${UNLOCKBASE_VARIABLE_ERROR};
			global ${UNLOCKBASE_VARIABLE_POINTERS};

			/* Do nothing if an error occurred previously */
			if (${UNLOCKBASE_VARIABLE_ERROR}) return;

			/* Remove the latest pointer */
			array_pop( ${UNLOCKBASE_VARIABLE_POINTERS} );
		}
		
		static function XML_CData ( $Parser, $Data )
		{
			/* Ignore whitespaces */
			if (rtrim($Data) == '') return;

			/* Globalize variables */
			global ${UNLOCKBASE_VARIABLE_ERROR};
			global ${UNLOCKBASE_VARIABLE_POINTERS};

			/* Do nothing if an error occurred previously */
			if (${UNLOCKBASE_VARIABLE_ERROR}) return;
			
			/* Get the latest pointer */
			$Pointer =& ${UNLOCKBASE_VARIABLE_POINTERS} [ count( ${UNLOCKBASE_VARIABLE_POINTERS} ) -1 ];
			
			if (is_array($Pointer))
			{
				/* Unrecognized XML stream, should be null or string here */
				${UNLOCKBASE_VARIABLE_ERROR} = true;
				return;
			}
			
			/* Append the character data */
			$Pointer .= $Data;
		}
	}
?>