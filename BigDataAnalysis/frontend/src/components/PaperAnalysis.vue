<template>
  <div class="paper-analysis">
    <h2>论文关键词分析</h2>
    <div v-if="loading" class="loading">
      <el-skeleton :rows="10" animated />
    </div>
    <div v-else-if="error" class="error">
      <el-alert :title="error" type="error" show-icon />
    </div>
    <div v-else-if="analysisData" class="analysis-results">
      <el-tabs type="border-card">
        <el-tab-pane label="TextRank关键词">
          <div class="keyword-section">
            <h3>TextRank关键词提取 <el-tooltip content="基于图排序的TextRank算法提取的关键词"><i class="el-icon-question"></i></el-tooltip></h3>
            <div class="keyword-cloud">
              <el-tag
                v-for="(item, index) in analysisData.textrank_keywords"
                :key="'tr-' + index"
                :type="getTagType(index)"
                :effect="index < 5 ? 'dark' : 'light'"
                class="keyword-tag"
                :style="{ fontSize: `${Math.min(16 + item.score * 10, 24)}px` }"
              >
                {{ item.keyword }}
                <span class="score">({{ item.score.toFixed(2) }})</span>
              </el-tag>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="TF-IDF关键词">
          <div class="keyword-section">
            <h3>TF-IDF关键词提取 <el-tooltip content="基于词频-逆文档频率的关键词提取"><i class="el-icon-question"></i></el-tooltip></h3>
            <div class="keyword-cloud">
              <el-tag
                v-for="(item, index) in analysisData.tfidf_keywords"
                :key="'tf-' + index"
                :type="getTagType(index)"
                :effect="index < 5 ? 'dark' : 'light'"
                class="keyword-tag"
                :style="{ fontSize: `${Math.min(16 + item.score * 10, 24)}px` }"
              >
                {{ item.keyword }}
                <span class="score">({{ item.score.toFixed(2) }})</span>
              </el-tag>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="词频统计">
          <div class="keyword-section">
            <h3>词频统计 <el-tooltip content="按出现频率排序的关键词"><i class="el-icon-question"></i></el-tooltip></h3>
            <div class="keyword-cloud">
              <el-tag
                v-for="(item, index) in analysisData.frequency_keywords"
                :key="'freq-' + index"
                :type="getTagType(index)"
                :effect="index < 5 ? 'dark' : 'light'"
                class="keyword-tag"
                :style="{ fontSize: `${Math.min(16 + item.score/5, 24)}px` }"
              >
                {{ item.keyword }}
                <span class="score">({{ item.score }})</span>
              </el-tag>
            </div>
          </div>
          
          <div class="top-keywords">
            <h3>热门词汇Top10</h3>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-table :data="analysisData.top10_keywords" stripe>
                  <el-table-column prop="word" label="词汇" />
                  <el-table-column prop="count" label="出现次数" />
                </el-table>
              </el-col>
              <el-col :span="12">
                <div class="chart-container" ref="keywordChart"></div>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="词性分析">
          <div class="keyword-section">
            <h3>基于词性的关键词 <el-tooltip content="根据词性（名词、动词等）提取的关键词"><i class="el-icon-question"></i></el-tooltip></h3>
            <div class="keyword-cloud">
              <el-tag
                v-for="(item, index) in analysisData.pos_keywords"
                :key="'pos-' + index"
                :type="getTagType(index)"
                :effect="index < 3 ? 'dark' : 'light'"
                class="keyword-tag"
                :style="{ fontSize: `${Math.min(16 + item.score * 3, 24)}px` }"
              >
                {{ item.keyword }}
                <span class="score">({{ item.score }})</span>
              </el-tag>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { paperAnalyze } from '../api'

export default {
  name: 'PaperAnalysis',
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
      analysisData: null,
      chart: null,
      tagTypes: ['', 'success', 'warning', 'danger', 'info']
    }
  },
  watch: {
    text: {
      handler(newVal) {
        if (newVal && newVal.trim()) {
          this.analyzeKeywords()
        }
      },
      immediate: true
    },
    'analysisData.top10_keywords': {
      handler() {
        this.$nextTick(() => {
          this.renderChart()
        })
      },
      deep: true
    }
  },
  methods: {
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
    },
    getTagType(index) {
      return this.tagTypes[index % this.tagTypes.length]
    },
    async analyzeKeywords() {
      if (!this.text || !this.text.trim()) return
      
      this.loading = true
      this.error = ''
      
      try {
        // 修改为使用text参数
        this.analysisData = await paperAnalyze({
          text: this.text
        })
        
        // 渲染图表
        this.$nextTick(() => {
          this.renderChart()
        })
      } catch (err) {
        this.error = '论文分析失败: ' + (err.message || '未知错误')
        console.error('论文分析错误:', err)
      } finally {
        this.loading = false
      }
    },
    renderChart() {
      if (!this.analysisData || !this.analysisData.top10_keywords || !this.$refs.keywordChart) return
      
      if (!this.chart) {
        this.chart = echarts.init(this.$refs.keywordChart)
      }
      
      const data = this.analysisData.top10_keywords.map(item => ({
        name: item.word,
        value: item.count
      }))
      
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c}'
        },
        series: [
          {
            type: 'pie',
            radius: '70%',
            data: data,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              show: true,
              formatter: '{b}: {c}'
            }
          }
        ]
      }
      
      this.chart.setOption(option)
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
.paper-analysis {
  margin: 20px 0;
}
.keyword-section {
  margin-bottom: 30px;
}
.keyword-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 15px;
}
.keyword-tag {
  margin: 5px;
  transition: all 0.3s;
}
.keyword-tag:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.score {
  font-size: 0.8em;
  opacity: 0.7;
  margin-left: 3px;
}
.top-keywords {
  margin-top: 30px;
}
.chart-container {
  height: 300px;
  margin-top: 20px;
}
.loading, .error {
  margin: 20px 0;
}
h3 {
  border-left: 4px solid #409EFF;
  padding-left: 10px;
  margin: 15px 0;
  font-weight: 500;
}
</style> 