<template>
  <div>
    <el-row>
      <el-col :span="3">
        <div style="text-align: center">字段序号</div>
      </el-col>
      <el-col :span="5">
        <div style="text-align: center">字段名称</div>
      </el-col>
      <el-col :span="4">
        <div style="text-align: center">是否为码内容</div>
      </el-col>
      <el-col :span="4">
        <div style="text-align: center">字段长度</div>
      </el-col>
      <el-col :span="6">
        <div style="text-align: center">验证匹配符</div>
      </el-col>
      <el-col :span="2" v-show="scope.mode==='add'||scope.mode==='edit'">
        <div style="text-align: center">操作</div>
      </el-col>
    </el-row>
    <el-form :model="currentForm" ref="currentFormRef" label-width="0px" size="mini" type="flex">
      <el-row style="margin-bottom: 0px" :gutter="5" v-for="(field, index) in currentForm.fieldList" :key="index">
        <el-col :span="3">
          <el-form-item  :prop="'fieldList.' + index + '.number'">
          <el-input-number style="width: 100%" controls-position="right" v-model="field.number" :disabled="scope.mode==='view'" :min="-1" :max="99"></el-input-number>
          </el-form-item>
        </el-col>
        <el-col :span="5">
          <el-form-item
            :prop="'fieldList.' + index + '.name'"
            :rules="[
                { required: true, message: '不能为空', trigger: 'blur' },
              ]"
          >
            <el-input v-model="field.name" :disabled="scope.mode==='view'" placeholder="请输入字段名称"></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="3" :offset="1" justify="center">
          <el-form-item
            :prop="'fieldList.' + index + '.is_code_content'"
            :rules="[
                { required: true, message: '不能为空', trigger: 'blur' }
              ]"
          >
            <el-switch
              v-model="field.is_code_content"
              active-text="是"
              inactive-text="否">
            </el-switch>
           </el-form-item>
        </el-col>
        <el-col :span="4">
          <el-form-item
            :prop="'fieldList.' + index + '.char_length'"
            :rules="[
                { required: true, message: '不能为空', trigger: 'blur' }
              ]"
          >
            <el-input-number style="width: 100%" controls-position="right" v-model="field.char_length" :disabled="scope.mode==='view'" :min="-1" :max="99"></el-input-number>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item
            :prop="'fieldList.' + index + '.verify_matches'"
            :rules="[
                { required: false, message: '不能为空', trigger: 'blur' }
              ]"
          >
            <el-input v-model="field.verify_matches" :disabled="scope.mode==='view'" placeholder="请输入验证匹配符"
                      clearable></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="2" v-show="scope.mode==='add'||scope.mode==='edit'">
          <el-form-item>
          <el-button @click.prevent="removeDomain(field)">删除</el-button>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item>
<!--        <el-button type="primary" @click="submitForm('dynamicValidateForm')">提交</el-button>-->
        <el-col :span="12" v-show="scope.mode==='add'||scope.mode==='edit'">
          <el-button type="primary" @click="addDomain">新增</el-button>
          <el-button @click="resetForm('currentFormRef')">重置</el-button>
        </el-col>
      </el-form-item>
    </el-form>
    <div>
      <el-alert

        type="error">
        <div style="line-height: 1.5em">
          <template slot:title>
            <span style="font-size: 1.2em">说明</span>
          </template>
          <div>1.匹配符为字符中包含(或左匹配);</div>
          <div>2.根据字段属性,自动生成字段数;</div>
          <div> 3.字段长度-1时,不验证;</div>
          <div>4.匹配符为空,不验证;</div>
        </div>
        </el-alert>
    </div>
  </div>
</template>

<script>
import XEUtils from 'xe-utils'
export default {
  name: 'attrFieldForm',
  props: {
    scope: {
      type: Object
    },
    formData: {
      type: Object,
      default () {
        return {
          fieldList: [{
            number: 0,
            name: '',
            char_length: '',
            is_code_content: false,
            verify_matches: ''
          }]
        }
      }
    }
  },
  computed: {
    currentForm () {
      this.formData.fieldList = XEUtils.orderBy(this.formData.fieldList, 'number')
      return this.formData
    }
  },
  data () {
    return {}
  },
  methods: {
    submitForm () {
      let res = ''
      this.$refs.currentFormRef.validate((valid) => {
        if (valid) {
          // alert('submit!')
          const { fieldList } = this.currentForm
          if (fieldList.some(item => { return item.is_code_content })) {
            res = fieldList
          } else {
            this.$message.error('字段属性中必须包含码内容!')
            return false
          }

          // return true
        } else {
          console.log('error submit!!')
          return false
        }
      })
      return res
    },
    resetForm (formName) {
      this.$refs[formName].resetFields()
    },
    removeDomain (item) {
      var index = this.currentForm.fieldList.indexOf(item)
      if (index !== -1) {
        this.currentForm.fieldList.splice(index, 1)
      }
      this.scope.form.fields = this.currentForm.fieldList.length
    },
    addDomain () {
      let index = this.currentForm.fieldList.length
      if (this.scope.mode === 'edit') {
        index = index + 1
      }
      this.currentForm.fieldList.push({
        number: index,
        name: '',
        char_length: '',
        is_code_content: false,
        verify_matches: ''
      })
      this.scope.form.fields = this.currentForm.fieldList.length
    }
  }
}
</script>

<style scoped>

</style>
