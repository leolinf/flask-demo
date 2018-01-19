;(function(){
    'use strict';
    angular
        .module( 'App.Account', []);
})();

;(function(){
    'use strict';

    angular
        .module( 'App.Account' )
        .controller( 'SignInCtrl', SignInCtrl );

    SignInCtrl.$inject = ['AccountService', 'ErrorHandler', 'Code', '$state', 'localStorageService','md5'];

    function SignInCtrl(AccountService,ErrorHandler,Code,$state,localStorageService,md5){
        // jshint validthis: true
        var vm = this;
        vm.signIn = signIn;
        vm.enterLogin = function(e) {
            if (e.keyCode == 13) signIn();
        };

        /**
         * 登录
         */
        function signIn() {
            if(typeof vm.username === 'string') vm.username = vm.username.trim();
            if(typeof vm.password === 'string') vm.password = vm.password.trim();

            if(!vm.username) {
                vm.errMsg = '用户名不能为空!';
                return false;
            }
            if(!vm.password) {
                vm.errMsg = '密码不能为空!';
                return false;
            }

            var params = {
                username    : vm.username,
                password    : md5.createHash(vm.password+ 'yhhx')
            };
            AccountService.signIn(params)
            .then(function(res) {
                if (res.code === Code.SUCCESS) {
                    localStorageService.set('username', vm.username);
                    $state.go('App.potential');
                }else if(res.code === Code.AUTH_FAILED) {
                    vm.errMsg = '用户名或密码错误!';
                }
            });
        }
    }
})();

/**
 * 需要图形短信验证码登录
 */
;(function(){
    'use strict';

    angular
        .module( 'App.Account' )
        .controller( 'SignInWithVerifyCtrl', SignInWithVerifyCtrl );

    SignInWithVerifyCtrl.$inject = [ 'AccountService', 'ErrorHandler', 'ToolsService', 'Code', '$state', 'localStorageService','md5', '$interval' ];

    function SignInWithVerifyCtrl( AccountService, ErrorHandler, ToolsService, Code, $state, localStorageService, md5, $interval ){
        // jshint validthis: true
        var vm                  = this;
        vm.signIn               = signIn;
        vm.getImgVerifyCode     = getImgVerifyCode;
        vm.getPhoneVerifyCode   = getPhoneVerifyCode;
        
        var countStart          = 60;
        vm.count                = countStart;           // 倒計時開始時間

        vm.enterLogin = function(e) {
            if (e.keyCode == 13) signIn();
        };

        init();

        function init(){
            vm.getImgVerifyCode();
        }

        /**
         * 登录
         */
        function signIn() {
            if(typeof vm.username === 'string') vm.username = vm.username.trim();
            if(typeof vm.password === 'string') vm.password = vm.password.trim();
            if( typeof vm.phoneVerifyCode !== 'undefined' ) vm.phoneVerify = vm.phoneVerifyCode.trim();
            if( !vm.username ) {
                vm.errMsg = '用户名不能为空!';
                return false;
            }
            if( !vm.password ) {
                vm.errMsg = '密码不能为空!';
                return false;
            }
            if( !vm.phoneVerifyCode ){
                vm.errMsg = 'phone verifycode not found!';
                return false;
            }

            var params = {
                username: vm.username,
                verifyCode  : vm.phoneVerifyCode,
                password: md5.createHash(vm.password+ 'yhhx')
            };
            AccountService.signIn(params)
            .then(function(res) {
                if (res.code === Code.SUCCESS) {
                    localStorageService.set('username', vm.username);
                    $state.go('App.potential');
                }else if(res.code === Code.AUTH_FAILED) {
                    vm.errMsg = '用户名或密码错误!';
                }
            });
        }

        /**
         * get image verifycode
         */
        function getImgVerifyCode(){
            AccountService.getImgVerifyCode()
            .then( function( res ){
                if( res.code === Code.SUCCESS ){
                    vm.imgVerifyCode = 'data:image/jpeg;charset=utf-8;base64,' + res.data.img;
                }
            });
        }

        /**
         * get phone verifycode
         */
        function getPhoneVerifyCode(){
            if( vm.username && vm.imgVerifyCodeStr && vm.count === countStart ){
                var params = {
                    phone       : vm.username,
                    verifyCode  : vm.imgVerifyCodeStr
                };
                AccountService.getPhoneVerifyCode( params )
                .then( function( res ){
                    if( res.code === Code.SUCCESS ){
                        console.log( 'get phone verify code success' );
                    }else{
                        console.log( 'get phone verify code failed' );
                    }
                });
                // countdown 60s
                ToolsService.countdown( countStart, 1, 1000, vm );
            }
        }

        /**
         * countdown function
         * @params {Number} count   - count start
         * @params {Number} step    - each count 
         * @params {Number} timeInterval - each execute interval
         * @params {Object} obj     - must have a attribute of count, used for transfer value outside function
         */
        /*
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
                    }
                    count -= step;
                    obj.count = count;
                }, timeInterval );
            }
        }
        */
    }
})();

;(function(){
    'use strict';

    angular
        .module( 'App.Account' )
        .service( 'AccountService', AccountService );

    AccountService.$inject = [ '$http' ];

    function AccountService( $http ){
        return {
            signIn              : signIn,
            getImgVerifyCode    : getImgVerifyCode,
            getPhoneVerifyCode  : getPhoneVerifyCode,
        };

        /**
         * signIn
         * @params {String} username - username
         * @params {String} password - user password after md5
         */
        function signIn( params ){
            return $http.post( '/api/sign_in/', params )
            .then( function( response ){
                return response.data;
            });
        }

        /**
         * get image verify code 
         */
        function getImgVerifyCode(){
            return $http.get( '/api/verify_pic/' )
            .then( function( response ){
                return response.data;
            });
        }

        /**
         * get phone verify code
         */
        function getPhoneVerifyCode( params ){
            return $http.post( '/api/sms/', params )
            .then( function( response ){
                return response.data;
            });
        }
    }
})();
