import { request } from '@/api/service'

export const urlPrefix = '/api/carton/production_manage/production_work/'

export function GetList (query) {
  return request({
    url: urlPrefix,
    method: 'get',
    params: query
  })
}

export function GetObj (obj) {
  return request({
    url: urlPrefix + obj.id + '/',
    method: 'get'
  })
}

export function createObj (obj) {
  return request({
    url: urlPrefix,
    method: 'post',
    data: obj
  })
}

export function UpdateObj (obj) {
  return request({
    url: urlPrefix + obj.id + '/',
    method: 'put',
    data: obj
  })
}

export function DelObj (id) {
  return request({
    url: urlPrefix + id + '/',
    method: 'delete',
    data: { id }
  })
}
/**
 * 获取生产报告
 * @param {*} params
 * @returns
 */
export function getProductionReport (params) {
  return request({
    url: urlPrefix + params.id + '/production_report/',
    method: 'get'
  })
}
