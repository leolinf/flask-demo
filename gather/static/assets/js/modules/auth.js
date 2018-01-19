;(function(){
    'use strict';
    angular
        .module( 'App.Auth', []);
})();

;(function(){
    'use strict';
    angular
        .module( 'App.Auth' )
		.controller( 'AuthDataDetailCtrl', AuthDataDetailCtrl );

	AuthDataDetailCtrl.$inject = [ 'AuthService', '$scope', '$interval', 'ErrorHandler', 'Code', '$stateParams', '$state' ];

	function AuthDataDetailCtrl( AuthService, $scope, $interval, ErrorHandler,Code, $stateParams, $state ){
        // jshint validthis: true
        var vm = this;

		var params	= $stateParams.params,
			sign	= $stateParams.sign

		if( !params || !sign ){
		}else{
			$state.go( 'AuthFormData', {} );
		}
		
		function getData(){
			AuthService.getData({
				params	: params,
				sign	: sign
			}).then( function( res ){
				if( res.code === Code.SUCCESS ){
					alert( 'get data success' );
					console.log( res.data );
				}else{
					alert( res.code );
				}
			});
		}
	}
})();

;(function(){
    'use strict';
    angular
        .module( 'App.Auth' )
		.controller( 'AuthFormDataCtrl', AuthFormDataCtrl );

	AuthFormDataCtrl.$inject = [ 'AuthService', '$scope' ];

	function AuthFormDataCtrl( AuthService, $scope ){
        // jshint validthis: true
        var vm = this;
	}
})();

;(function(){
    'use strict';
    angular
        .module( 'App.Auth' )
		.factory( 'AuthService', AuthService );

	AuthService.$inject = [ '$http' ];

	function AuthService( $http ){
		return {
			getData			: getData
		};

		/**
		 * 获取授权数据
		 */
		function getData( params ){
			return $http.post( '/api/getData', params )
			.then( function( response ){
				return response.data;
			});
		}
	}
})();
