;(function(){
    'use strict';

    angular
        .module( 'App.Const', [] );
})();

;(function(){
    'use strict';

    angular
        .module( 'App.Const' )
        .constant( 'Default', {
         
        });
})();

;(function(){
    'use strict';

    angular
        .module( 'App.Const' )
        .constant( 'Code', {
            SUCCESS					: 10000,
			TOEKN_NEEDED			: 20001,
			PERMISSION_DENIED		: 41499,
			NETWORK_ERROR			: 41500,
			NETWORK_ERROR_1			: 41501,
			// PARAMS_NEED			: 41502,
			SYSTEM_ERROR			: 41502,
			QUERY_TIMEOUT			: 41503,
			QUERYING				: 41504,
			NO_DATA					: 41505,
			NOT_EXIST				: 41506,
			AUTH_FAILED				: 41507,
			DATA_GETTING			: 41508,
			GET_CODE_FAILED			: 41510,
			AUTH_FAILED_1			: 41511,
			LOGIN_ERROR				: 41512,
			VERIFY_CODE_ERROR		: 41513,
			ACCOUNT_FAILED			: 41514,
			VERIFY_CODE_FREQUENCY	: 41515,
			VERIFY_CODE_LIMIT		: 41516,
			SYSTEM_ERROR_1			: 50000
        })
		.constant( 'CodeMsg', {
			'41499'	: '权限不足，请联系我们',
			'41500'	: '网络异常，请稍后重试',
			'41501'	: '网络异常，请稍后重试',
			'41502'	: '服务器出错了，请稍后重试',
			'41503'	: '请求超时，请稍后重试',
			'41504'	: '数据查询中，请耐心等待',
			'41505'	: '查询成功无数据',
			'41506'	: '帐号不存在或未开通手机登录，请检查后再试',
			'41507'	: '授权失败，请稍后重试',
			'41508'	: '正在获取数据，请稍后再授权',
			'41510'	: '短信验证码发送失败，请稍后重试',
			'41511'	: '授权失败，请稍后重试',
			'41512'	: '登录异常，请稍后重试',
			'41513'	: '短信验证码错误或过期，请重新获取',
			'41514'	: '账号异常，请15分钟后重试',
			'41515'	: '发送短信过于频繁，请15分钟后再试',
			'41516'	: '发送短信次数达到上限，请明天再试',
			'50000'	: '服务器出错了，请稍后'
		});
})();
