'use strict';

/**
 * AnalyticsController controller for "analytics"
 */
analyticsModule
.controller(
		'AnalyticsController',
		[
		 '$scope',
		 '$rootScope',
		 '$state',
		 '$stateParams',
		 '$timeout',
		 '$filter',
		 '$http',
		 function($scope, $rootScope, $state, $stateParams,
				 $timeout, $filter, $http) {

			 $scope.waitingForPlot = false;

			 console.log("BB-Insights!");
			 updateNodeRedSources();
			 $scope.nodered = {
					 url : "...Endpoint URL unknown..."
			 };
			 // $scope.selectedSource = {url:"", name: "",
			 // initialLabel: "Select your data source here"};

			 /**
			  * 
			  * Get the endpoint URL for Node-RED. This is used for the "Open Node-RED" button 
			  * 
			  * */
			 $http
			 .get('api_analytics/nrendpoint')
			 .then(
					 function successCallback(response) {
						 console.log("endpoint is at: "
								 + response.data.url);
						 $scope.nodered = {
								 url : response.data.url
						 };
						 if (!response.data.url) {
							 $rootScope
							 .$broadcast(
									 'FlashMessage',
									 {
										 "type" : "danger",
										 "text" : "Error communicating with analytics back end"
									 });
						 }
					 },
					 function errorCallback(response) {
						 $rootScope
						 .$broadcast(
								 'FlashMessage',
								 {
									 "type" : "danger",
									 "text" : "Error communicating with analytics back end: "
										 + response
								 });
					 });
			 /**
			  * 
			  * Draws the plot. Get the data from backend and run bokeh
			  * 
			  * */

			 $scope.drawPlot = function(plotType) {
				 $scope.bbTableData = undefined;
				 $scope.waitingForPlot = true;
				 $http
				 .get('api_analytics/plot',
						 {
					 params : {
						 "nrDataSource" : $filter('urlEncode')($scope.selectedSource),
						 "plotType"		: $filter('urlEncode')(plotType)
					 }
						 })
						 .then(
								 function successCallback(
										 response) {
									 console.log(response.data);

									 if (!response.data) {
										 $rootScope
										 .$broadcast(
												 'FlashMessage',
												 {
													 "type" : "danger",
													 "text" : "No data received from backend"
												 });
										 $scope.waitingForPlot = false;
										 return;
									 }


									 $scope.bbplot = response.data[1];
									 $scope.waitingForPlot = false;
									 // There has to be a better
									 // way...
									 setTimeout(function() {
										 try {
											 eval(response.data[0]);
										 } catch (e) {
											 console.log(e);
											 $rootScope
											 .$broadcast(
													 'FlashMessage',
													 {
														 "type" : "danger",
														 "text" : "Bokeh frontend could not display the data."
													 });
											 $scope.waitingForPlot = false;
											 $scope.bbplot = undefined;
										 }


									 }, 100);


								 },
								 function errorCallback(response) {
									 $scope.waitingForPlot = false;
									 console
									 .log(JSON
											 .stringify(response));
									 if (420 == response.status) {

									 }
									 $rootScope
									 .$broadcast(
											 'FlashMessage',
											 {
												 "type" : "danger",
												 "text" : "Error: "
													 + response.data,
													 timeout : 30000
											 });
								 });

			 };
			 /**
			  * 
			  * Draws the plot. Get the data from backend and run bokeh
			  * 
			  * */

			 $scope.showResultTable = function() {
				 $scope.bbplot = undefined;
				 $scope.waitingForPlot = true;
				 $http
				 .get('api_analytics/table',
						 {
					 params : {
						 "nrDataSource" : $filter('urlEncode')($scope.selectedSource)
					 }
						 })
						 .then(
								 function successCallback(response) {
									 console.log(response);
									 if (!response.data.table) {
										 $rootScope
										 .$broadcast(
												 'FlashMessage',
												 {
													 "type" : "danger",
													 "text" : "No data received from backend"
												 });
										 $scope.waitingForPlot = false;
										 return;
									 }
									 $scope.bbTableData = {
											 table : JSON.parse(response.data.table),
											 info : response.data.info,
											 truncated : response.data.truncated
											 };
									 //console.log($scope.bbTableData);
									 $scope.waitingForPlot = false;
								 },
								 function errorCallback(response) {
									 $scope.waitingForPlot = false;
									 console.log(JSON.stringify(response));
									 if (420 == response.status) {

									 }
									 $rootScope
									 .$broadcast(
											 'FlashMessage',
											 {
												 "type" : "danger",
												 "text" : "Error: "
													 + response.data,
													 timeout : 30000
											 });
								 });

			 };

			 /**
			  * 
			  * Get the list of Node-RED endoints for the list
			  * 
			  * */
			 $scope.updateNodeRedSources = updateNodeRedSources;
			 function updateNodeRedSources() {
				 $http
				 .get('api_analytics/nrsources')
				 .then(
						 function successCallback(
								 response) {
							 console.log(response.data);
							 $scope.availableSources = response.data;

							 if (!response.data) {
								 $rootScope
								 .$broadcast(
										 'FlashMessage',
										 {
											 "type" : "danger",
											 "text" : "unable to retrieve Node-RED enpoint list..."
										 });
							 }
						 },
						 function errorCallback(response) {
							 console
							 .log(JSON
									 .stringify(response));
							 $rootScope
							 .$broadcast(
									 'FlashMessage',
									 {
										 "type" : "danger",
										 "text" : "Error: "
											 + response.data
									 });
						 });

			 }
			 ;
		 } ]);