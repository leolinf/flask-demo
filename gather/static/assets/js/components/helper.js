;(function(){
    'use strict';

    angular
        .module( 'Helper', [] );
})();

;(function(){
    'use strict';

    angular
        .module( 'Helper' )
        .service( 'ErrorHandler', ErrorHandler );

    ErrorHandler.$inject = [ 'Code', '$state' ];

    function ErrorHandler( Code, $state ){
        return function( response, cb ){
            switch( response.code ){
                case Code.SUCCESS:
                    cb( response );
                    break;
                case Code.AUTH_FAILED:
                    $state.go('Signin');
                    break;
                default:
                    cb( response );
            }
        };
    }
})();

;(function(){
    'use strict';

    angular
        .module( 'Helper' )
        .service( 'ToolsService', ToolsService );

    ToolsService.$inject = [ '$interval' ];

    function ToolsService( $interval ){
        return {
            countdown   : countdown,
			noEmpty		: noEmpty,
        };

        /**
         * countdown function
         * @params {Number} count   - count start
         * @params {Number} step    - each count 
         * @params {Number} timeInterval - each execute interval
         * @params {Object} obj     - must have a attribute of count, used for transfer value outside function, usually obj is vm 
         */
        function countdown( count, step, timeInterval, obj ){
            var countStart = count;

            count -= step;
            obj.count = count;
            if( count > 0 ){
                var interval = $interval( function(){
                    if( count === 0 ){
                        $interval.cancel( interval );
                        interval = undefined;
                        obj.count = countStart;
                    }else{
                        count -= step;
                        obj.count = count;
                    }
                }, timeInterval );
            }
        }

		/**
		 * 处理传入参数为空的情况
		 */
		function noEmpty( value ){
			if( value ){
				return value;
			}else{
				return '--';
			}
		}
    }
})();

;(function(){
    'use strict';

    angular 
        .module( 'Helper' )
        .service( 'ValidatorService', ValidatorService );

    ValidatorService.$inject = [];

    function ValidatorService(){
        return {
            username    : username,
            password    : password
        };

        /**
         * 验证用户名
         * @param {String} name - 要验证的用户名
         * @returns {Boolean} - 符合规则返回真,否则返回假
         */
        function username( name ){
            var regex = /^[a-zA-Z0-9]{6,20}$/;
            return regex.test( name );
        }

        /**
         * 验证密码
         * @param {String} passwd - 要验证的密码
         * @returns {Boolean} - 符合规则返回真,否则返回假
         */
        function password( passwd ){
            var regex = /^[a-zA-Z0-9]{6,20}$/;
            return regex.test( passwd );
        }
    }
})();
