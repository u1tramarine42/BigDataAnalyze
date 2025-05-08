<template>
  <div class="topic-analysis">
    <h2>主题分析</h2>
    <div v-if="loading" class="loading">
      <el-loading :visible="loading" text="分析中..."></el-loading>
    </div>
    <div v-else-if="error" class="error">
      <el-alert :title="error" type="error"></el-alert>
    </div>
    <div v-else-if="topicData">
      <el-card v-for="(topic, index) in topicData" :key="index" class="topic-card">
        <template #header>
          <div class="topic-header">
            <span>主题 {{ index + 1 }}</span>
          </div>
        </template>
        <div class="keywords">
          <el-tag 
            v-for="(keyword, kidx) in topic" 
            :key="kidx"
            class="keyword-tag"
            :type="tagTypes[kidx % tagTypes.length]">
            {{ keyword }}
          </el-tag>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { topicAnalyze } from '../api'

export default {
  name: 'TopicAnalysis',
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
      topicData: null,
      tagTypes: ['', 'success', 'warning', 'danger', 'info']
    }
  },
  watch: {
    text: {
      handler(newVal) {
        if (newVal && newVal.trim()) {
          this.analyzeTopics()
        }
      },
      immediate: true
    }
  },
  methods: {
    async analyzeTopics() {
      if (!this.text || !this.text.trim()) return
      
      this.loading = true
      this.error = ''
      
      try {
        this.topicData = await topicAnalyze(this.text)
      } catch (err) {
        this.error = '主题分析失败: ' + (err.message || '未知错误')
        console.error('主题分析错误:', err)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.topic-analysis {
  margin: 20px 0;
}
.topic-card {
  margin-bottom: 20px;
}
.topic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.keywords {
  display: flex;
  flex-wrap: wrap;
}
.keyword-tag {
  margin: 5px;
  font-size: 14px;
}
.loading, .error {
  margin-top: 20px;
}
</style> 