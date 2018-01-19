;(function(){
    'use strict';

    angular
        .module( 'App', [
            'ui.router',
            // 'ui.bootstrap',
            'angular-md5',
            'ngRap',
            'ngAnimate',
            'LocalStorageModule',
            'Helper',
            'App.Const',
            // 'App.Account',
			'App.Auth',
        ] );
})();

;(function(){
    'use strict';

    angular
        .module( 'App' )
        .config( config )
        .run( init );

    init.$inject = [ '$rootScope', '$state', '$stateParams', 'localStorageService' ];

    function init( $rootScope, $state, $stateParams, localStorageService ){
        $rootScope.$state       = $state;
        $rootScope.$stateParams = $stateParams;

        $rootScope.$on('$stateChangeSuccess',function(event,toState,toParams,fromState,fromParams){
            $rootScope.prevState        = fromState;
            $rootScope.prevStateParams  = fromParams;
        });
    }

    config.$inject = [ '$locationProvider', '$stateProvider', '$urlRouterProvider', '$httpProvider', 'ngRapProvider' ];
    
    function config( $locationProvider, $stateProvider, $urlRouterProvider, $httpProvider, ngRapProvider ){
        // ngRapProvider.script = 'http://rap.taobao.org/rap.plugin.js?projectId=15607';
        // ngRapProvider.enable({
        //     mode: 3
        // });
        // $httpProvider.interceptors.push( 'rapMockInterceptor' );

        $stateProvider
			/*
            .state( 'SignIn', {
                url             : '/signin',
                templateUrl     : '/templates/modules/account/sign_in.tpl.html',
                controller      : 'SignInCtrl',
                controllerAs    : 'vm'
            })
			*/
			.state( 'AuthFormData', {
				url				: '/auth_form_data/',
				templateUrl		: '/templates/modules/auth/form_data.tpl.html',
				controller		: 'AuthFormDataCtrl',
				controllerAs	: 'vm'
			})
			.state( 'AuthDataDetail', {
				url				: '/auth_data_detail/?params&sign',
				templateUrl		: '/templates/modules/auth/detail.tpl.html',
				controller		: 'AuthDataDetailCtrl',
				controllerAs	: 'vm'
			});

		$locationProvider.html5Mode( true );
		//每一个请求都带上token
		// $httpProvider.interceptors.push( injectToken );
    }

    // injectToken.$inject = [ '$q', '$location', 'localStorageService' ];

    /*
    function injectToken( $q, $location, localStorageService ){
		return {
			'request':function(config){
				
				config.headers = config.headers || {};
				var token = localStorageService.get( 'token' );
				if(token && token.trim() !== ''){
					config.headers.token = token;
				}
				return config;
				
			},
			'responseError':function(response){
				if(response.status === 401 || response.status === 403){
					window.location = '';
				}
				return $q.reject(response);
			}
		};
    }
    */
})();
