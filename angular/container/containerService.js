'use strict';

containerModule.factory(
    'containerService',
    ['$http', '$httpParamSerializer', '$q', '$filter', 'Upload', function($http, $httpParamSerializer, $q, $filter, Upload) {
        return {
            getObjectsInContainer: function(containerName) {
                var deferred = $q.defer();
                $http.get('/swift/containers/' + containerName + '/objects')
                    .then(function successCallback(response) {
                            deferred.resolve(response.data);
                        }, function errorCallback(response) {
                            deferred.reject(response);
                        }
                    );

                return deferred.promise;
            },

            deleteObject: function(containerName, objectName) {
                var deferred = $q.defer();
                $http.delete('/swift/containers/' + containerName + '/objects/' + $filter('urlEncode')(objectName))
                    .then(function successCallback(response) {
                            deferred.resolve(response.data);
                        }, function errorCallback(response) {
                            deferred.reject(response);
                        }
                    );

                return deferred.promise;
            },

            upload: function(file, containerName, ownerName, retentionDate) {
                var deferred = $q.defer();
                Upload.upload({
                    "method": "POST",
                    "url": "/upload",
                    "data": {
                        "objectName":       file,
                        "containerNameUp":  containerName,
                        "OwnerName":        ownerName ? ownerName : "",
                        "RetentionPeriod":  retentionDate ? retentionDate : ""
                    }
                }).then(function successCallback(response) {
                        deferred.resolve(response.data);
                    }, function errorCallback(response) {
                        deferred.reject(response);
                    }
                );

                return deferred.promise;
            }
        };
    }]);