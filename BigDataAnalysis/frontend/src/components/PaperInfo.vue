<template>
  <div class="paper-info">
    <h2>论文信息提取</h2>
    <div v-if="loading" class="loading">
      <el-skeleton :rows="10" animated />
    </div>
    <div v-else-if="error" class="error">
      <el-alert :title="error" type="error" show-icon />
    </div>
    <div v-else-if="paperInfo" class="paper-details">
      <el-descriptions border direction="vertical" :column="1" size="large">
        <el-descriptions-item label="题目" label-align="left" label-class-name="label-left">
          <el-tag type="primary" size="large" effect="dark">{{ paperInfo.题目 || paperInfo.标题 || '未提取到' }}</el-tag>
        </el-descriptions-item>
        
        <el-descriptions-item label="作者" label-align="left" label-class-name="label-left">
          <template v-if="paperInfo.作者 && paperInfo.作者.length">
            <el-tag 
              v-for="(author, index) in paperInfo.作者" 
              :key="index"
              type="success"
              effect="plain"
              style="margin-right: 8px; margin-bottom: 5px;"
            >
              {{ author }}
            </el-tag>
          </template>
          <span v-else>未提取到</span>
        </el-descriptions-item>
        
        <el-descriptions-item label="发表单位" label-align="left" label-class-name="label-left">
          <template v-if="paperInfo.发表单位">
            <div class="institution-content">1. {{ paperInfo.发表单位 }}</div>
          </template>
          <span v-else>未提取到</span>
        </el-descriptions-item>
        
        <el-descriptions-item label="分类号" label-align="left" label-class-name="label-left">
          <el-tag type="info" v-if="paperInfo.分类号">{{ paperInfo.分类号 }}</el-tag>
          <el-tag type="info" v-else-if="paperInfo.中图分类号">{{ paperInfo.中图分类号 }}</el-tag>
          <span v-else>未提取到</span>
        </el-descriptions-item>
        
        <el-descriptions-item label="文献标志码" label-align="left" label-class-name="label-left">
          <el-tag type="info" v-if="paperInfo.文献标志码">{{ paperInfo.文献标志码 }}</el-tag>
          <el-tag type="info" v-else-if="paperInfo.文献标识码">{{ paperInfo.文献标识码 }}</el-tag>
          <span v-else>未提取到</span>
        </el-descriptions-item>
        
        <el-descriptions-item label="关键词" label-align="left" label-class-name="label-left">
          <div v-if="paperInfo.关键词 && paperInfo.关键词.length" class="keywords-container">
            <el-tag
              v-for="(keyword, index) in paperInfo.关键词"
              :key="index"
              :type="index % 4 === 0 ? 'danger' : index % 3 === 0 ? 'warning' : index % 2 === 0 ? 'success' : 'primary'"
              style="margin-right: 8px; margin-bottom: 5px;"
            >
              {{ keyword }}
            </el-tag>
          </div>
          <span v-else>未提取到</span>
        </el-descriptions-item>
        
        <el-descriptions-item label="摘要" label-align="left" label-class-name="label-left">
          <div class="abstract-content">
            {{ paperInfo.摘要 || '未提取到' }}
          </div>
        </el-descriptions-item>
        
        <el-descriptions-item label="参考文献" label-align="left" label-class-name="label-left">
          <template v-if="paperInfo.参考文献 && paperInfo.参考文献.length">
            <el-collapse>
              <el-collapse-item title="查看参考文献" name="1">
                <div class="ref-list">
                  <div v-for="(ref, index) in cleanReferences(paperInfo.参考文献)" :key="index" class="ref-item">
                    {{ ref }}
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </template>
          <span v-else>未提取到</span>
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script>
import { extractPaperInfo } from '../api'

export default {
  name: 'PaperInfo',
  props: {
    text: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      loading: false,
      error: '',
      paperInfo: null
    }
  },
  watch: {
    text: {
      handler(newVal) {
        if (newVal && newVal.trim()) {
          this.extractInfo()
        }
      },
      immediate: true
    }
  },
  methods: {
    cleanReferences(references) {
      if (!references || !references.length) return []
      // 移除参考文献前的序号（如"1."）
      return references.map(ref => {
        // 移除开头的数字序号和点号
        return ref.replace(/^\s*\d+\.\s*/, '')
      })
    },
    async extractInfo() {
      if (!this.text || !this.text.trim()) return
      
      this.loading = true
      this.error = ''
      
      try {
        this.paperInfo = await extractPaperInfo(this.text)
        console.log('接收到的论文信息:', this.paperInfo)
      } catch (err) {
        this.error = '论文信息提取失败: ' + (err.message || '未知错误')
        console.error('论文信息提取错误:', err)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.paper-info {
  margin: 20px 0;
}
.paper-details {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.keywords-container {
  display: flex;
  flex-wrap: wrap;
}
.abstract-content {
  text-indent: 2em;
  line-height: 1.6;
  color: #333;
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  border-left: 4px solid #409EFF;
}
.institution-content {
  line-height: 1.6;
  color: #333;
}
.ref-list {
  padding-left: 0;
  line-height: 1.6;
}
.ref-item {
  margin-bottom: 8px;
  color: #606266;
  padding: 5px 0;
  border-bottom: 1px dashed #ebeef5;
}
.loading, .error {
  margin: 20px 0;
}
/* 添加标签左对齐样式 */
:deep(.label-left) {
  justify-content: flex-start !important;
  padding-left: 20px !important;
}
</style> 