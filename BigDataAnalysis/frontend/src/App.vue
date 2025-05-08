<template>
  <div id="app">
    <el-container>
      <el-header class="app-header">
        <div class="logo-container">
          <img src="@/assets/logo-analysis.svg" alt="论文可视化系统" class="logo" />
          <h1>论文可视化系统</h1>
        </div>
        <div class="header-actions">
          <el-tooltip content="切换主题" placement="bottom">
            <el-button circle icon="el-icon-moon" @click="toggleTheme"></el-button>
          </el-tooltip>
        </div>
      </el-header>
      
      <el-main>
        <el-card class="input-card" shadow="hover">
          <template #header>
            <div class="input-header">
              <h2><i class="el-icon-document"></i> 论文内容</h2>
              <div class="header-actions">
                <el-upload
                  class="upload-demo"
                  action="#"
                  :auto-upload="false"
                  :show-file-list="false"
                  :on-change="handleFileUpload"
                  :before-upload="beforeFileUpload"
                  accept=".txt,.pdf,.docx,.doc"
                >
                  <el-tooltip content="支持TXT、PDF和Word文档" placement="top">
                    <el-button size="small" type="primary" icon="el-icon-upload">
                      导入文件
                    </el-button>
                  </el-tooltip>
                </el-upload>
                <div class="upload-tip">支持格式：TXT、PDF和Word文档(DOCX优先)</div>
              </div>
            </div>
          </template>
          <el-form>
            <el-form-item>
              <el-input
                v-model="paperText"
                type="textarea"
                :rows="15"
                :autosize="{ minRows: 10, maxRows: 30 }"
                placeholder="请在此处粘贴论文内容（包括标题、摘要、正文等）或导入文件..."
                resize="both"
                class="paper-textarea"
              ></el-input>
            </el-form-item>
            <el-form-item class="action-buttons">
              <el-button 
                type="primary" 
                @click="analyze" 
                :loading="isAnalyzing" 
                size="large" 
                icon="el-icon-data-analysis"
              >
                分析
              </el-button>
              <el-button @click="clearInput" size="large" icon="el-icon-delete">清空</el-button>
              <el-button 
                type="success" 
                @click="loadSample" 
                size="large" 
                icon="el-icon-document-copy"
              >
                加载示例
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <div v-if="analyzed" class="analysis-results">
          <el-tabs type="border-card">
            <el-tab-pane label="情感分析">
              <EmotionAnalysis :text="paperText" />
            </el-tab-pane>
            <el-tab-pane label="主题分析">
              <TopicAnalysis :text="paperText" />
            </el-tab-pane>
            <el-tab-pane label="关键词分析">
              <PaperAnalysis :text="paperText" />
            </el-tab-pane>
            <el-tab-pane label="论文信息">
              <PaperInfo :text="paperText" />
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- 文件上传处理中的加载对话框 -->
        <el-dialog
          title="文件处理中"
          v-model="showLoadingDialog"
          width="300px"
          center
          :show-close="false"
          :close-on-click-modal="false"
          :close-on-press-escape="false"
        >
          <div class="loading-dialog-content">
            <el-progress type="circle" :percentage="processingProgress"></el-progress>
            <p>{{ processingMessage }}</p>
          </div>
        </el-dialog>

        <!-- 添加文件上传对话框 -->
        <el-dialog
          title="选择编码"
          v-model="showEncodingDialog"
          width="400px"
          center
          :show-close="false"
          :close-on-click-modal="false"
          :close-on-press-escape="false"
        >
          <div class="encoding-selection">
            <p>如果导入的文件出现乱码，请选择适合的编码格式：</p>
            <el-radio-group v-model="selectedEncoding">
              <div><el-radio label="utf-8">UTF-8</el-radio></div>
              <div><el-radio label="gbk">GB2312/GBK</el-radio></div>
              <div><el-radio label="gb18030">GB18030</el-radio></div>
              <div><el-radio label="windows-1252">Windows-1252</el-radio></div>
              <div><el-radio label="iso-8859-1">ISO-8859-1</el-radio></div>
            </el-radio-group>
          </div>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="cancelReload">取消</el-button>
              <el-button type="primary" @click="reloadWithEncoding">确定</el-button>
            </span>
          </template>
        </el-dialog>
      </el-main>
      
      <el-footer>
        <p>&copy; 202205Z 基于知网学术论文的文本数据可视化 版权所有：李祎晨，付祉宁，钱张枫</p>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import EmotionAnalysis from './components/EmotionAnalysis.vue'
import TopicAnalysis from './components/TopicAnalysis.vue'
import PaperAnalysis from './components/PaperAnalysis.vue'
import PaperInfo from './components/PaperInfo.vue'
import mammoth from 'mammoth'

// 示例论文内容
const SAMPLE_PAPER = `人工智能驱动的教育变革与创新
张明 李华 王芳
北京大学 计算机科学与技术学院 上海交通大学 教育学院

摘要: 随着人工智能技术的快速发展，其在教育领域的应用正引发深刻变革。本文探讨了人工智能在个性化学习、智能评估和教育管理等方面的创新应用，分析了AI教育工具对学习过程的影响，并对未来教育发展趋势进行了展望。研究表明，AI技术能够有效提升学习效率，促进教育公平，但同时也带来了数据隐私保护、算法偏见等伦理挑战。为充分发挥AI教育的积极作用，需要构建合理的技术应用框架，加强师资培训，并制定相关政策标准，以实现技术与教育的深度融合，推动教育系统的可持续创新发展。

关键词: 人工智能; 教育创新; 个性化学习; 智能评估; 教育伦理

中图分类号: G434 文献标志码: A

在当今数字化时代，信息技术的发展为各领域带来了革命性变化，教育作为社会发展的基础，正日益受到人工智能技术的深刻影响。人工智能(Artificial Intelligence, AI)通过模拟、延伸和扩展人类智能，为教育系统注入了新的活力，正在改变传统的教学模式、学习方式和教育管理流程。

一、人工智能在教育中的应用现状
近年来，各种AI驱动的教育工具和平台快速涌现，主要应用场景包括：个性化学习系统能够根据学生的学习风格、知识掌握程度和学习习惯，自动调整教学内容和进度；智能辅导系统可提供即时反馈和指导，弥补传统课堂中教师难以关注到每个学生需求的不足；自动评分系统不仅能对客观题进行评判，也逐渐具备了评估论文、口语表达等主观性内容的能力。

二、人工智能对教育流程的重构
人工智能技术正在重塑教育的各个环节。在课前准备阶段，AI系统可分析学生的知识图谱，为教师提供教学建议；课堂教学中，智能系统可实时监测学生的注意力和理解程度，辅助教师调整教学策略；课后评估环节，AI技术能够提供多维度的学习分析，形成个性化的学习报告和改进方案。这种全流程的智能支持，使得教育过程更加精准高效。

三、人工智能教育的伦理与挑战
尽管AI教育工具展现出巨大潜力，但其应用也面临诸多挑战和伦理问题。数据隐私保护是首要考虑因素，学生的学习数据收集和使用需建立在严格的伦理框架之下；算法公平性也是关键问题，需防止AI系统中的潜在偏见对不同背景学生造成不公平影响；此外，过度依赖技术可能导致人际互动减少，不利于学生社交能力和情感发展。

结语：人工智能正成为推动教育创新的重要力量，未来的教育生态将是人机协作的智能环境。为更好地发挥AI的教育价值，需加强政策引导、伦理规范和技术研发，构建面向未来的智能教育新模式。

参考文献：
[1] 王建, 张静. 人工智能教育应用的现状与展望[J]. 远程教育杂志, 2021, 39(3): 34-41.
[2] Baker R S, Inventado P S. Educational data mining and learning analytics[M]. Springer, 2020.
[3] Li X, Wang T. Exploring the Ethical Implications of AI in Education[J]. Ethics and Information Technology, 2022: 1-15.`

export default {
  name: 'App',
  components: {
    EmotionAnalysis,
    TopicAnalysis,
    PaperAnalysis,
    PaperInfo
  },
  data() {
    return {
      paperText: '',
      isAnalyzing: false,
      analyzed: false,
      darkMode: false,
      // 文件上传相关参数
      currentFile: null,
      showEncodingDialog: false,
      selectedEncoding: 'utf-8',
      // 文件处理加载状态
      showLoadingDialog: false,
      processingProgress: 0,
      processingMessage: '正在处理文件，请稍候...'
    }
  },
  computed: {
    canImport() {
      return this.currentFile !== null;
    }
  },
  methods: {
    analyze() {
      if (!this.paperText.trim()) {
        this.$message({
          message: '请先输入论文内容',
          type: 'warning'
        })
        return
      }
      
      this.isAnalyzing = true
      
      // 模拟分析过程
      setTimeout(() => {
        this.isAnalyzing = false
        this.analyzed = true
        this.$message({
          message: '分析完成！',
          type: 'success'
        })
      }, 500)
    },
    clearInput() {
      this.paperText = ''
      this.analyzed = false
      this.$message({
        message: '内容已清空',
        type: 'info'
      })
    },
    loadSample() {
      this.paperText = SAMPLE_PAPER
      this.$message({
        message: '已加载示例论文',
        type: 'success'
      })
    },
    beforeFileUpload(file) {
      const isTooLarge = file.size / 1024 / 1024 > 20;
      if (isTooLarge) {
        this.$message.error('文件大小不能超过20MB!');
        return false;
      }
      
      // 检查文件类型
      const fileName = file.name.toLowerCase();
      if (!fileName.endsWith('.txt') && !fileName.endsWith('.pdf') && 
          !fileName.endsWith('.doc') && !fileName.endsWith('.docx')) {
        this.$message.error('仅支持TXT、PDF和Word文档格式');
        return false;
      }
      
      return true;
    },
    async handleFileUpload(file) {
      this.currentFile = file.raw;
      const fileName = file.name.toLowerCase();
      
      this.showLoadingDialog = true;
      this.processingProgress = 0;
      this.processingMessage = '正在处理文件，请稍候...';
      
      try {
        if (fileName.endsWith('.txt')) {
          await this.handleTxtFile(file.raw);
        } else if (fileName.endsWith('.pdf')) {
          await this.handlePdfFile(file.raw);
        } else if (fileName.endsWith('.doc') || fileName.endsWith('.docx')) {
          await this.handleWordFile(file.raw);
        } else {
          throw new Error('不支持的文件格式');
        }
      } catch (error) {
        this.$message.error('文件处理失败: ' + error.message);
        console.error('文件处理错误:', error);
      } finally {
        this.showLoadingDialog = false;
      }
    },
    async handleTxtFile(file) {
      this.processingMessage = '正在读取TXT文件...';
      this.processingProgress = 30;
      
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            this.processingProgress = 70;
            this.paperText = e.target.result;
            
            // 检测编码问题
            if (this.hasEncodingIssues(this.paperText)) {
              this.showEncodingDialog = true;
            } else {
              this.$message.success('TXT文件导入成功');
            }
            
            this.processingProgress = 100;
            resolve();
          } catch (error) {
            reject(error);
          }
        };
        
        reader.onerror = (error) => {
          reject(error);
        };
        
        // 使用UTF-8编码读取
        reader.readAsText(file, 'UTF-8');
      });
    },
    // 检测编码问题
    hasEncodingIssues(text) {
      // 检查乱码的常见特征
      const unusualSymbolsRatio = (text.match(/[^\u4e00-\u9fa5a-zA-Z0-9，。；：""''！？、（）《》【】\s]/g) || []).length / text.length;
      const hasWeirdSymbols = /[\ufffd\uf8f8\uf7f7\uf6f6\uf5f5]/.test(text); // 检查常见乱码符号
      
      // 如果异常符号比例高于30%或者包含常见乱码符号，则可能是编码问题
      return unusualSymbolsRatio > 0.3 || hasWeirdSymbols;
    },
    async handlePdfFile(file) {
      this.processingMessage = '正在解析PDF文件...';
      this.processingProgress = 20;
      
      try {
        // 确保PDF.js可用
        if (!window.pdfjsLib) {
          window.pdfjsLib = window.pdfjsLib || window.PDFJS;
        }
        
        if (!window.pdfjsLib) {
          throw new Error('PDF.js库未加载，请检查网络连接');
        }
        
        // 配置worker
        if (!window.pdfjsLib.GlobalWorkerOptions.workerSrc) {
          window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';
        }
        
        // 将File对象转换为ArrayBuffer
        const arrayBuffer = await this.readFileAsArrayBuffer(file);
        this.processingProgress = 30;
        
        // 加载PDF文档
        const loadingTask = window.pdfjsLib.getDocument(arrayBuffer);
        const pdf = await loadingTask.promise;
        this.processingProgress = 50;
        
        // 提取所有页面的文本
        let textContent = [];
        const numPages = pdf.numPages;
        
        for (let i = 1; i <= numPages; i++) {
          this.processingMessage = `正在处理第 ${i}/${numPages} 页...`;
          this.processingProgress = 50 + Math.floor((i / numPages) * 40);
          
          // 获取页面
          const page = await pdf.getPage(i);
          
          // 提取文本内容
          const content = await page.getTextContent();
          
          // 将文本项转换为字符串
          const pageText = content.items.map(item => item.str).join(' ');
          textContent.push(pageText);
        }
        
        this.paperText = textContent.join('\n\n');
        this.processingProgress = 100;
        this.$message.success('PDF文件导入成功');
      } catch (error) {
        console.error('处理PDF文件出错:', error);
        throw new Error('PDF文件解析失败: ' + error.message);
      }
    },
    async handleWordFile(file) {
      this.processingMessage = '正在解析Word文档...';
      this.processingProgress = 20;
      
      try {
        const arrayBuffer = await this.readFileAsArrayBuffer(file);
        this.processingProgress = 40;
        
        // 检查文件扩展名
        if (file.name.toLowerCase().endsWith('.docx')) {
          // 处理DOCX格式 (用mammoth处理)
          const result = await mammoth.extractRawText({ arrayBuffer });
          this.processingProgress = 80;
          this.paperText = result.value;
        } else {
          // 处理DOC格式 (旧版Word格式)
          // 注意：mammoth主要支持.docx文件，对于.doc文件可能需要先转换
          try {
            // 尝试用mammoth处理
            const result = await mammoth.extractRawText({ arrayBuffer });
            this.processingProgress = 80;
            this.paperText = result.value;
          } catch (docError) {
            // 如果处理失败，提示用户
            throw new Error('无法处理旧版Word文档(.doc)，请将文档另存为.docx格式后重试，或复制文档内容到输入框');
          }
        }
        
        this.processingProgress = 100;
        this.$message.success('Word文档导入成功');
      } catch (error) {
        console.error('处理Word文档出错:', error);
        throw new Error(error.message || 'Word文档解析失败');
      }
    },
    readFileAsArrayBuffer(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(e);
        reader.readAsArrayBuffer(file);
      });
    },
    cancelReload() {
      this.showEncodingDialog = false;
    },
    reloadWithEncoding() {
      if (!this.currentFile) {
        this.showEncodingDialog = false;
        return;
      }
      
      this.showLoadingDialog = true;
      this.processingProgress = 30;
      this.processingMessage = '正在使用所选编码重新读取文件...';
      
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          this.paperText = e.target.result;
          this.processingProgress = 100;
          this.$message.success('文件已使用' + this.selectedEncoding + '编码重新导入');
        } catch (error) {
          this.$message.error('文件读取失败: ' + error.message);
        } finally {
          this.showEncodingDialog = false;
          this.showLoadingDialog = false;
        }
      };
      
      reader.onerror = () => {
        this.$message.error('文件读取失败');
        this.showEncodingDialog = false;
        this.showLoadingDialog = false;
      };
      
      reader.readAsText(this.currentFile, this.selectedEncoding);
    },
    toggleTheme() {
      this.darkMode = !this.darkMode
      document.body.classList.toggle('dark-theme', this.darkMode)
      this.$message({
        message: `已切换到${this.darkMode ? '暗黑' : '明亮'}主题`,
        type: 'success'
      })
    }
  }
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
  background-color: #f5f7fa;
  transition: all 0.3s ease;
}

body.dark-theme {
  background-color: #121212;
  color: #e0e0e0;
}

#app {
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Microsoft YaHei", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #409EFF 0%, #007aff 100%);
  color: white;
  padding: 0 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  height: 60px;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.logo-container {
  display: flex;
  align-items: center;
}

.logo {
  height: 40px;
  margin-right: 10px;
}

.el-main {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.el-footer {
  background-color: #f7f7f7;
  color: #606266;
  text-align: center;
  line-height: 60px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

.input-card {
  margin-bottom: 30px;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.input-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
}

.header-actions {
  display: flex;
  align-items: center;
}

.paper-textarea {
  font-size: 14px;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
}

.analysis-results {
  margin-top: 30px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.08);
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 深色主题适配 */
.dark-theme .el-card,
.dark-theme .el-tabs,
.dark-theme .el-table {
  background-color: #1e1e1e;
  color: #e0e0e0;
  border-color: #333;
}

.dark-theme .el-tabs__header {
  background-color: #2c2c2c;
}

.dark-theme .el-footer {
  background-color: #1a1a1a;
  color: #aaa;
}

.dark-theme .el-input__inner,
.dark-theme .el-textarea__inner {
  background-color: #2c2c2c;
  border-color: #444;
  color: #e0e0e0;
}

.dark-theme .el-card__header {
  border-bottom: 1px solid #444;
}

.dark-theme h1, 
.dark-theme h2, 
.dark-theme h3 {
  color: #e0e0e0;
}

/* 响应式适配 */
@media screen and (max-width: 768px) {
  .el-main {
    padding: 10px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .app-header {
    padding: 0 10px;
  }
  
  .logo {
    height: 30px;
  }
  
  h1 {
    font-size: 18px;
  }
}

.encoding-selection {
  padding: 10px 0;
}
.encoding-selection p {
  margin-bottom: 15px;
  color: #606266;
}
.encoding-selection .el-radio {
  margin-bottom: 10px;
  display: block;
}

.el-upload {
  display: inline-block;
}
.el-upload__tip {
  line-height: 1.5;
  color: #909399;
  font-size: 12px;
  margin-top: 5px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-left: 10px;
}

/* 添加处理对话框样式 */
.loading-dialog-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 0;
}

.loading-dialog-content p {
  margin-top: 15px;
  color: #606266;
}
</style>
