export const crudOptions = (vm) => {
  return {
    pageOptions: {
      compact: true
    },
    options: {
      tableType: 'vxe-table',
      rowKey: true, // 必须设置，true or false
      rowId: 'id',
      height: '100%', // 表格高度100%, 使用toolbar必须设置
      highlightCurrentRow: false

    },
    rowHandle: {
      width: 110,
      fixed: 'right',
      view: false,
      edit: false,
      remove: false,
      custom: [
        {
          thin: true,
          text: '问题码记录',
          size: 'small',
          type: 'warning',
          emit: 'onErrorCode'
        }
      ]
    },
    viewOptions: {
      componentType: 'row'
    },
    formOptions: {
      defaultSpan: 12 // 默认的表单 span
    },
    indexRow: { // 或者直接传true,不显示title，不居中
      title: '序号',
      align: 'center',
      width: 80
    },
    columns: [
      {
        title: '关键词',
        key: 'search',
        show: false,
        disabled: true,
        search: {
          disabled: false
        },
        form: {
          disabled: true,
          component: {
            placeholder: '请输入关键词'
          }
        },
        view: {
          disabled: true
        }
      }, {
        title: 'ID',
        key: 'id',
        show: false,
        form: {
          disabled: true
        }
      }, {
        title: '相机编号',
        key: 'no',
        minWidth: 100,
        search: {
          disabled: false,
          component: {
            placeholder: '请输入相机编号',
            clearable: true
          }
        },
        type: 'input',
        form: {
          disabled: true
        }
      },
      {
        title: '设备名称',
        key: 'device_name',
        minWidth: 160,
        search: {
          disabled: false,
          component: {
            placeholder: '请输入设备名称',
            clearable: true
          }
        },
        form: {
          disabled: true
        }
      },
      {
        title: '工厂名称',
        key: 'factory_name',
        minWidth: 160,
        search: {
          disabled: false,
          component: {
            placeholder: '请输入工厂名称',
            clearable: true
          }
        },
        form: {
          disabled: true
        }
      },
      {
        title: '产线名称',
        key: 'prod_line_name',
        minWidth: 160,
        search: {
          disabled: false,
          component: {
            placeholder: '请输入产线名称',
            clearable: true
          }
        },
        form: {
          disabled: true
        }
      },
      {
        title: '识别码总数',
        key: 'need_number',
        minWidth: 100,
        type: 'number',
        search: {
          disabled: true
        },
        form: {
          disabled: true
        }
      },
      {
        title: '识别成功数',
        key: 'success_number',
        type: 'number',
        minWidth: 100
      },
      {
        title: '成功采集率',
        key: 'success_rate',
        type: 'number',
        minWidth: 160,
        component: {
          name: 'table-progress'
        }
      },
      {
        title: '未识别码数',
        key: 'unrecognized_num',
        minWidth: 100,
        type: 'number',
        search: {
          disabled: true
        },
        form: {
          disabled: true
        }
      }, {
        title: '不存在码数',
        key: 'code_not_exist_num',
        minWidth: 100,
        type: 'number',
        search: {
          disabled: true
        },
        form: {
          disabled: true
        }
      }, {
        title: '本检测包重码数',
        key: 'self_repetition_num',
        minWidth: 140,
        type: 'number',
        search: {
          disabled: true
        },
        form: {
          disabled: true
        }
      },
      {
        title: '本生产工单重码数',
        key: 'prod_repetition_num',
        minWidth: 140,
        type: 'number',
        search: {
          disabled: true
        },
        form: {
          disabled: true
        }
      },
      {
        title: '非本生产工单码数',
        key: 'prod_wrong_num',
        minWidth: 140,
        type: 'number',
        search: {
          disabled: true
        },
        form: {
          disabled: true
        }
      }

    ].concat(vm.commonEndColumns({
      update_datetime: { showTable: false }
    }))
  }
}
