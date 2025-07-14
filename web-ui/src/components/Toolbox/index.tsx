import React, { useState } from 'react';
import { Card, Row, Col, Input, Button, Upload, message, Typography, Alert } from 'antd';
import { SearchOutlined, EyeOutlined, UploadOutlined } from '@ant-design/icons';
import { templateApi } from '@/services/api';
import type { TemplateMatchResult } from '@/types';

const { Title, Text } = Typography;

const Toolbox: React.FC = () => {
  const [templateName, setTemplateName] = useState('');
  const [templateResult, setTemplateResult] = useState<TemplateMatchResult | null>(null);
  const [templateLoading, setTemplateLoading] = useState(false);
  const [ocrResult, setOcrResult] = useState('');
  const [ocrLoading, setOcrLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFindTemplate = async () => {
    if (!templateName.trim()) {
      message.warning('请输入模板名称');
      return;
    }

    setTemplateLoading(true);
    try {
      const response = await templateApi.find({ template_name: templateName });
      if (response.success && response.data) {
        setTemplateResult(response.data);
        message.success('模板匹配成功');
      } else {
        setTemplateResult(null);
        message.warning('未找到匹配的模板');
      }
    } catch (error) {
      message.error('模板匹配失败');
      setTemplateResult(null);
    } finally {
      setTemplateLoading(false);
    }
  };

  const handleOcrRecognize = async () => {
    if (!selectedFile) {
      message.warning('请选择图片文件');
      return;
    }

    setOcrLoading(true);
    try {
      // 这里需要先上传文件到服务器，然后调用OCR接口
      // 由于原始API需要image_path，这里先显示开发中的提示
      message.info('OCR功能开发中，需要先实现文件上传接口');
      setOcrResult('OCR功能开发中...');
    } catch (error) {
      message.error('OCR识别失败');
    } finally {
      setOcrLoading(false);
    }
  };

  const beforeUpload = (file: File) => {
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error('只能上传图片文件');
      return false;
    }
    
    const isLt10M = file.size / 1024 / 1024 < 10;
    if (!isLt10M) {
      message.error('图片大小不能超过10MB');
      return false;
    }

    setSelectedFile(file);
    return false; // 阻止自动上传
  };

  return (
    <div>
      <Title level={2}>工具箱</Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card
            title={
              <span>
                <SearchOutlined style={{ marginRight: '8px' }} />
                模板匹配
              </span>
            }
            style={{ height: '400px' }}
          >
            <div style={{ marginBottom: '16px' }}>
              <Input
                placeholder="请输入模板名称"
                value={templateName}
                onChange={(e) => setTemplateName(e.target.value)}
                onPressEnter={handleFindTemplate}
                style={{ marginBottom: '12px' }}
              />
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={handleFindTemplate}
                loading={templateLoading}
                block
              >
                查找模板
              </Button>
            </div>
            
            {templateResult && (
              <Alert
                message="找到模板!"
                description={
                  <div>
                    <div><Text strong>置信度:</Text> {(templateResult.confidence * 100).toFixed(2)}%</div>
                    <div><Text strong>位置:</Text> ({templateResult.location[0]}, {templateResult.location[1]})</div>
                    <div><Text strong>大小:</Text> {templateResult.size[0]} × {templateResult.size[1]}</div>
                    <div><Text strong>中心点:</Text> ({templateResult.center[0]}, {templateResult.center[1]})</div>
                  </div>
                }
                type="success"
                style={{ marginTop: '16px' }}
              />
            )}
            
            {templateResult === null && templateName && !templateLoading && (
              <Alert
                message="未找到模板"
                description="请检查模板名称是否正确，或确认模板文件是否存在"
                type="warning"
                style={{ marginTop: '16px' }}
              />
            )}
          </Card>
        </Col>
        
        <Col xs={24} lg={12}>
          <Card
            title={
              <span>
                <EyeOutlined style={{ marginRight: '8px' }} />
                OCR文字识别
              </span>
            }
            style={{ height: '400px' }}
          >
            <div style={{ marginBottom: '16px' }}>
              <Upload
                beforeUpload={beforeUpload}
                accept="image/*"
                showUploadList={false}
                style={{ marginBottom: '12px' }}
              >
                <Button icon={<UploadOutlined />} block>
                  {selectedFile ? selectedFile.name : '选择图片文件'}
                </Button>
              </Upload>
              <Button
                type="primary"
                icon={<EyeOutlined />}
                onClick={handleOcrRecognize}
                loading={ocrLoading}
                disabled={!selectedFile}
                block
              >
                识别文字
              </Button>
            </div>
            
            {ocrResult && (
              <div
                style={{
                  border: '1px solid #d9d9d9',
                  borderRadius: '6px',
                  padding: '12px',
                  backgroundColor: '#fafafa',
                  minHeight: '100px',
                  maxHeight: '200px',
                  overflowY: 'auto'
                }}
              >
                <Text strong>识别结果:</Text>
                <div style={{ marginTop: '8px', whiteSpace: 'pre-wrap' }}>
                  {ocrResult}
                </div>
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Toolbox;