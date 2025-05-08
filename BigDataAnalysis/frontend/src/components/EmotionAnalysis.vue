<template>
  <div class="emotion-analysis">
    <h2>情感分析</h2>
    <div class="description">
      <el-alert
        title="情感分析结果展示"
        type="info"
        description="此分析展示文本中六种情感倾向（困惑、批判、支持、中立、预期、惊讶）的分布情况，使用雷达图直观呈现。"
        show-icon
        :closable="false"
      />
    </div>
    
    <div class="chart-container" ref="emotionChart"></div>
    
    <div v-if="emotionData" class="emotion-stats">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" v-for="(value, emotion) in emotionData" :key="emotion">
          <el-card shadow="hover" class="emotion-card" :class="getEmotionClass(emotion)">
            <div class="emotion-header">
              <span class="emotion-name">{{ getEmotionName(emotion) }}</span>
              <el-progress 
                type="dashboard" 
                :percentage="calculatePercentage(value)" 
                :color="getEmotionColor(emotion)" 
                :stroke-width="8"
              />
            </div>
            <div class="emotion-value">
              <span class="value">{{ value }}</span>
              <span class="label">情感强度</span>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <div v-if="loading" class="loading">
      <el-skeleton :rows="5" animated />
    </div>
    
    <div v-if="error" class="error">
      <el-alert :title="error" type="error" show-icon />
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { emotionAnalyze } from '../api'

const EMOTION_COLORS = {
  'Confused': '#FF9800',
  'Critical': '#F44336',
  'Supportive': '#4CAF50',
  'Neutral': '#2196F3',
  'Anticipatory': '#9C27B0',
  'Surprised': '#009688'
}

const EMOTION_NAMES = {
  'Confused': '困惑',
  'Critical': '批判',
  'Supportive': '支持',
  'Neutral': '中立',
  'Anticipatory': '预期',
  'Surprised': '惊讶'
}

export default {
  name: 'EmotionAnalysis',
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
      chart: null,
      emotionData: null
    }
  },
  watch: {
    text: {
      handler(newVal) {
        if (newVal && newVal.trim()) {
          this.analyzeEmotion()
        }
      },
      immediate: true
    }
  },
  methods: {
    getEmotionName(emotion) {
      return EMOTION_NAMES[emotion] || emotion
    },
    getEmotionColor(emotion) {
      return EMOTION_COLORS[emotion] || '#409EFF'
    },
    getEmotionClass(emotion) {
      return `emotion-${emotion.toLowerCase()}`
    },
    calculatePercentage(value) {
      if (!this.emotionData) return 0
      const max = Math.max(...Object.values(this.emotionData))
      return Math.round((value / (max || 1)) * 100)
    },
    async analyzeEmotion() {
      if (!this.text || !this.text.trim()) return
      
      this.loading = true
      this.error = ''
      
      try {
        this.emotionData = await emotionAnalyze(this.text)
        this.renderChart()
      } catch (err) {
        this.error = '情感分析失败: ' + (err.message || '未知错误')
        console.error('情感分析错误:', err)
      } finally {
        this.loading = false
      }
    },
    renderChart() {
      if (!this.emotionData) return
      
      // 确保DOM已渲染
      this.$nextTick(() => {
        if (!this.chart) {
          this.chart = echarts.init(this.$refs.emotionChart)
        }
        
        // 数据处理
        const emotions = Object.keys(this.emotionData)
        const values = emotions.map(key => this.emotionData[key])
        const max = Math.max(...values) || 10
        
        // 雷达图配置
        const option = {
          title: {
            text: '文本情感分析',
            textStyle: {
              fontSize: 18,
              fontWeight: 'bold'
            },
            left: 'center'
          },
          tooltip: {
            trigger: 'item',
            formatter: function(params) {
              const emotion = params.name
              const value = params.value
              return `${EMOTION_NAMES[emotion] || emotion}: ${value}`
            }
          },
          radar: {
            shape: 'circle',
            indicator: emotions.map(name => ({
              name: EMOTION_NAMES[name] || name,
              max: max
            })),
            splitArea: {
              areaStyle: {
                color: ['rgba(255, 255, 255, 0.2)'],
                shadowBlur: 10
              }
            },
            axisLine: {
              lineStyle: {
                color: 'rgba(64, 158, 255, 0.5)'
              }
            },
            splitLine: {
              lineStyle: {
                color: 'rgba(64, 158, 255, 0.3)'
              }
            }
          },
          series: [{
            name: '情感分布',
            type: 'radar',
            data: [{
              value: values,
              name: '情感强度',
              symbol: 'circle',
              symbolSize: 10,
              areaStyle: {
                color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
                  {
                    color: 'rgba(64, 158, 255, 0.8)',
                    offset: 0
                  },
                  {
                    color: 'rgba(64, 158, 255, 0.3)',
                    offset: 1
                  }
                ])
              },
              lineStyle: {
                width: 3
              },
              itemStyle: {
                color: '#409EFF'
              }
            }]
          }]
        }
        
        this.chart.setOption(option)
      })
    },
    debounce(fn, delay) {
      let timer = null;
      return function() {
        let context = this;
        let args = arguments;
        clearTimeout(timer);
        timer = setTimeout(function() {
          fn.apply(context, args);
        }, delay);
      };
    }
  },
  mounted() {
    // 使用debounce优化resize事件处理
    const debouncedResize = this.debounce(() => {
      if (this.chart) {
        this.chart.resize();
      }
    }, 100);
    
    window.addEventListener('resize', debouncedResize);
    this.resizeHandler = debouncedResize; // 保存引用以便在beforeUnmount中移除
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.dispose();
      this.chart = null;
    }
    // 确保正确移除事件监听器
    if (this.resizeHandler) {
      window.removeEventListener('resize', this.resizeHandler);
    }
  }
}
</script>

<style scoped>
.emotion-analysis {
  margin: 20px 0;
}
.description {
  margin-bottom: 20px;
}
.chart-container {
  width: 100%;
  height: 400px;
  margin: 20px 0;
}
.emotion-stats {
  margin: 30px 0;
}
.emotion-card {
  margin-bottom: 20px;
  border-radius: 8px;
  transition: transform 0.3s ease;
  position: relative;
  overflow: hidden;
}
.emotion-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}
.emotion-card::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 10px;
  height: 100%;
  transition: opacity 0.3s;
}
.emotion-confused::after { background-color: #FF9800; }
.emotion-critical::after { background-color: #F44336; }
.emotion-supportive::after { background-color: #4CAF50; }
.emotion-neutral::after { background-color: #2196F3; }
.emotion-anticipatory::after { background-color: #9C27B0; }
.emotion-surprised::after { background-color: #009688; }

.emotion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.emotion-name {
  font-size: 18px;
  font-weight: 500;
}
.emotion-value {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 10px;
}
.emotion-value .value {
  font-size: 24px;
  font-weight: bold;
}
.emotion-value .label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}
.loading, .error {
  margin: 20px 0;
}
</style> 