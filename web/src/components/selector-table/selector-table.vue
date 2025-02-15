<template>
  <div ref="selectedTableRef">
    <el-popover
      placement="bottom"
      width="600"
      trigger="click"
      @show="visibleChange">
      <div class="option">
        <el-row>
          <el-col :span="21">
            <el-input
              style="margin-bottom: 10px"
              v-model="search"
              clearable
              size="small"
              placeholder="请输入关键词"
              @change="getDict"
              @clear="getDict">
              <el-button style="width: 100px" slot="append" icon="el-icon-search"></el-button>
            </el-input>
          </el-col>
          <el-col :span="3" style="padding-left: 10px;padding-right: 10px;">
            <el-button type="primary" round size="mini" style="padding: 10px;" @click="onClear">清空选择</el-button>
          </el-col>
        </el-row>
        <el-table
          ref="tableRef"
          :data="tableData"
          size="mini"
          border
          :row-key="dict.value"
          style="width: 600px"
          max-height="200"
          height="200"
          :highlight-current-row="!_elProps.tableConfig.multiple"
          @selection-change="handleSelectionChange"
          @row-click="handleCurrentChange"
        >
          <el-table-column v-if="_elProps.tableConfig.multiple" fixed type="selection" reserve-selection width="55"/>
          <el-table-column fixed type="index" label="#" width="50"/>
          <span v-for="(item,index) in _elProps.tableConfig.columns" :key="index" >
            <el-table-column :prop="item.prop" :label="item.label" :width="item.width"
                             v-if="item.show !== false">
              <template slot-scope="scope">
                <span v-if="item.type === 'image'">
                  <el-image :src="baseURL + scope.row[item.prop]" style="height: 30px;width: 30px;">
                    <div slot="placeholder" class="image-slot">
                      <img src="./loading-spin.svg">
                    </div>
                  </el-image>
                </span>
                <span v-else>{{ scope.row[item.prop] }}</span>
              </template>
            </el-table-column>
          </span>
        </el-table>
        <el-pagination style="margin-top: 10px;max-width: 200px" background
                       small
                       :current-page="pageConfig.page"
                       :page-size="pageConfig.limit"
                       layout="prev, pager, next"
                       :total="pageConfig.total"
                       @current-change="handlePageChange"
        />
      </div>
      <div slot="reference" ref="divRef" :style="{'pointerEvents': disabled?'none':''}">
        <div v-if="currentValue.length>0" class="div-input el-input__inner" :class="disabled?'div-disabled':''">
          <div v-if="currentValue instanceof Array">
            <el-tag
              style="margin-right: 5px"
              v-for="(item,index) in currentValue"
              :key="index"
              :closable="disabled"
              size="small"
              :hit="false"
              type="info"
              @close="itemClosed(item,index)"
              disable-transitions
            >
              <span>{{ item[dict.label] }}</span>
            </el-tag>
          </div>
        </div>
        <el-input v-else placeholder="请选择" slot:reference clearable :disabled="disabled" :size="size"></el-input>
      </div>
    </el-popover>
  </div>
</template>

<script>
import { request } from '@/api/service'
import XEUtils from 'xe-utils'
import { d2CrudPlus } from 'd2-crud-plus'
import util from '@/libs/util'

export default {
  name: 'selector-table-input',
  // model: {
  //   prop: 'value',
  //   event: ['change', 'input']
  // },
  mixins: [d2CrudPlus.input, d2CrudPlus.inputDict],
  props: {
    // 值
    value: {
      type: [String, Number, Array],
      required: false,
      default: ''
    },
    size: {
      type: String,
      required: false,
      default: ''
    },
    // 数据字典配置
    dict: {
      type: Object,
      require: false
    },
    // 其他配置
    elProps: {
      type: Object,
      require: false,
      default () {
        return {
          tableConfig: {
            pagination: true,
            multiple: false,
            columns: []
          }
        }
      }
    },
    // 你可以定义一些参数，通过component.props传进来
    color: {
      required: false
    },
    styleName: {
      type: [Object, String],
      required: false,
      default () {
        return {}
      }
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      // 由于value值是props参数，是不允许修改的，需要用别的值存起来
      currentValue: [],
      pageConfig: {
        page: 1,
        limit: 5,
        total: 0
      },
      search: null,
      tableData: [],
      multipleSelection: [],
      collapseTags: false,
      baseURL: util.baseURL()
    }
  },
  computed: {
    // 你也可以通过computed来监听value的变化，跟watch作用类似，根据实际情况选用
    _elProps () {
      return this.elProps
    }
  },
  watch: {
    // value (value) {
    //   // 父组件收到input事件后会通过v-model改变value参数的值
    //   // 然后此处会watch到value的改变，发出change事件
    //   // change事件放在此处发射的好处是，当外部修改value值时，也能够触发form-data-change事件
    //   this.$emit('change', value)
    //   // if (this.currentValue === value) {
    //   //   return
    //   // }
    //   // 如果值是被外部改变的，则修改本组件的currentValue
    //   // this.setCurrentValue(value)
    // },
    multipleSelection: {
      handler (newValue, oldVal) {
        const { tableConfig } = this._elProps
        // 是否多选
        if (tableConfig.multiple) {
          this.currentValue = newValue
        } else {
          this.currentValue = [newValue]
        }
      },
      deep: true,
      immediate: true
    }
  },
  mounted () {
    // 给currentValue设置初始值
    this.setCurrentValue(this.value)
  },
  methods: {
    // 设置显示值
    setCurrentValue (val) {
      const params = {}
      if (this._elProps.tableConfig.pagination) {
        params.page = this.pageConfig.page
        params.limit = this.pageConfig.limit
      }
      if (val && val.toString().length > 0) {
        // 在这里对 传入的value值做处理
        let { url, value, label } = this.dict
        params[value] = val
        const queryList = ['id', label, value]
        this._elProps.tableConfig.columns.map(res => {
          queryList.push(res.prop)
        })
        params.query = `{${Array.from(new Set(queryList)).join(',')}}`
        if (typeof url === 'function') {
          const form = this.d2CrudContext.getForm()
          url = url(this.dict, { form })
        }
        return request({
          url: url,
          params: params,
          method: 'get'
        }).then(res => {
          const { data, page, limit, total } = res
          this.pageConfig.page = page
          this.pageConfig.limit = limit
          this.pageConfig.total = total
          if (data.data && data.data.length > 0) {
            console.log(data.data)
            this.currentValue = data.data
          } else {
            this.currentValue = []
          }
        })
      } else {
        this.currentValue = []
      }
    },
    // 获取数据
    getDict () {
      const that = this
      const { value, label } = this.dict
      let url
      if (typeof that.dict.url === 'function') {
        const form = that.d2CrudContext.getForm()
        url = that.dict.url(that.dict, { form })
      } else {
        url = that.dict.url
      }
      let dictParams = {}
      if (that.dict.params) {
        dictParams = { ...that.dict.params }
      }
      const queryList = ['id', label, value]
      this._elProps.tableConfig.columns.map(res => {
        queryList.push(res.prop)
      })
      const params = {
        page: that.pageConfig.page,
        limit: that.pageConfig.limit,
        query: `{${Array.from(new Set(queryList)).join(',')}}`
      }
      if (that.search) {
        params.search = that.search
        params.page = 1
      }
      if (that._elProps.tableConfig.data === undefined || that._elProps.tableConfig.data.length === 0) {
        request({
          url: url,
          method: 'get',
          params: { ...params, ...dictParams }
        }).then(res => {
          const { data, page, limit, total } = res.data
          that.pageConfig.page = page
          that.pageConfig.limit = limit
          that.pageConfig.total = total
          if (that._elProps.tableConfig.isTree) {
            that.tableData = XEUtils.toArrayTree(data, { parentKey: 'parent', key: 'id', children: 'children' })
          } else {
            that.tableData = data
          }
        })
      } else {
        that.tableData = that._elProps.tableConfig.data
      }
    },
    /**
     * 下拉框展开/关闭
     * @param bool
     */
    visibleChange () {
      const that = this
      that.getDict()
      const { tableConfig } = that._elProps
      if (tableConfig.multiple) {
        that.$refs.tableRef.clearSelection() // 先清空选择,再赋值选择
        // eslint-disable-next-line no-unused-expressions
        that.currentValue ? that.currentValue.forEach(item => {
          that.$refs.tableRef.toggleRowSelection(item, true)
        }) : null
      }
    },
    /**
     * 分页
     * @param page
     */
    handlePageChange (page) {
      this.pageConfig.page = page
      this.getDict()
    },
    /**
     * 表格多选
     * @param val:Array
     */
    handleSelectionChange (val) {
      this.multipleSelection = val
      this.$emit('checkChange', val)
      const result = val.map((item) => {
        return item[this.dict.value]
      })
      if (this.dispatch) {
        this.dispatch('ElFormItem', 'el.form.blur')
      }
      this.$emit('input', result)
      this.$emit('change', result)
    },
    /**
     * 表格单选
     * @param val:Object
     */
    handleCurrentChange (val) {
      const { tableConfig } = this._elProps
      if (!tableConfig.multiple) {
        this.multipleSelection = val
        this.$emit('radioChange', val)
        if (this.dispatch) {
          this.dispatch('ElFormItem', 'el.form.blur')
        }
        this.$emit('input', val[this.dict.value])
        this.$emit('change', val[this.dict.value])
      }
    },
    /***
     * 清空
     */
    onClear () {
      const { tableConfig } = this._elProps
      if (!tableConfig.multiple) {
        this.$emit('input', '')
        this.$emit('change', '')
      } else {
        this.$emit('input', [])
        this.$emit('change', [])
      }
    },
    /**
     * tag删除事件
     * @param obj
     */
    itemClosed (obj, index) {
      const { tableConfig } = this._elProps
      XEUtils.remove(this.multipleSelection, index)
      XEUtils.remove(this.currentValue, index)
      if (!tableConfig.multiple) {
        this.$emit('input', '')
        this.$emit('change', '')
      } else {
        // eslint-disable-next-line no-unused-expressions
        this.$refs.tableRef?.toggleRowSelection(obj, false)
        // const { value } = this.dict
        // const result = this.currentValue.map((item) => {
        //   return item[value]
        // })
        // this.$emit('input', result)
        // this.$emit('change', result)
      }
    }
  }
}
</script>
<style scoped>
.option {
  height: auto;
  line-height: 1;
  padding: 5px;
  background-color: #fff;
}

</style>
<style lang="scss">
.popperClass {
  height: 320px;
}

.el-select-dropdown__wrap {
  max-height: 310px !important;
}

.tableSelector {
  .el-icon, .el-tag__close {
    display: none;
  }
}

.div-input {
  -webkit-appearance: none;
  background-color: #FFF;
  background-image: none;
  border-radius: 4px;
  border: 1px solid #DCDFE6;
  -webkit-box-sizing: border-box;
  box-sizing: border-box;
  color: #606266;
  display: inline-block;
  min-height: 40px;
  line-height: 40px;
  outline: 0;
  padding: 0 15px;
  -webkit-transition: border-color .2s cubic-bezier(.645, .045, .355, 1);
  transition: border-color .2s cubic-bezier(.645, .045, .355, 1);
  min-width: 120px;
}
.div-disabled{
  background-color: #F5F7FA;
  border-color: #E4E7ED;
  color: #C0C4CC;
  cursor: not-allowed;
  pointer-events: none;
}
</style>
