"""
Report Generation Agent - Creates detailed property reports with visualizations
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import io
from datetime import datetime
import os

class ReportAgent:
    """Agent for generating property reports and PDFs"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_LEFT
        ))
    
    def create_price_chart(self, properties):
        """Create price distribution chart"""
        prices = [p['price'] for p in properties if p.get('price', 0) > 0]
        
        if not prices:
            return None
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(prices, bins=10, color='#2c5aa0', alpha=0.7, edgecolor='black')
        ax.set_xlabel('Price', fontsize=12)
        ax.set_ylabel('Number of Properties', fontsize=12)
        ax.set_title('Price Distribution', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # Save to BytesIO
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def create_location_chart(self, properties):
        """Create location distribution chart"""
        locations = {}
        for p in properties:
            loc = p.get('location', 'Unknown')
            if loc and loc != 'Unknown':
                # Take first part of location (city/area)
                city = loc.split(',')[0].strip()
                locations[city] = locations.get(city, 0) + 1
        
        if not locations:
            return None
        
        # Top 10 locations
        sorted_locs = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]
        locs, counts = zip(*sorted_locs)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.barh(locs, counts, color='#4a90e2', alpha=0.7)
        ax.set_xlabel('Number of Properties', fontsize=12)
        ax.set_ylabel('Location', fontsize=12)
        ax.set_title('Top Locations', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        # Save to BytesIO
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def generate_summary_report(self, properties, stats, filename='property_report.pdf'):
        """
        Generate a comprehensive property summary report
        
        Args:
            properties: List of property dicts
            stats: Statistics dict
            filename: Output filename
        
        Returns:
            Path to generated PDF file
        """
        # Create output directory
        os.makedirs('reports', exist_ok=True)
        filepath = os.path.join('reports', filename)
        
        # Create PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        
        # Title
        title = Paragraph("Property Search Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Report metadata
        date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        meta = Paragraph(f"<i>Generated on {date_str}</i>", self.styles['CustomBody'])
        story.append(meta)
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        summary_title = Paragraph("Executive Summary", self.styles['CustomHeading'])
        story.append(summary_title)
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Properties', str(stats.get('total_properties', len(properties)))],
            ['Average Price', f"${stats.get('avg_price', 0):,.2f}"],
            ['Minimum Price', f"${stats.get('min_price', 0):,.2f}"],
            ['Maximum Price', f"${stats.get('max_price', 0):,.2f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Add charts
        if properties:
            # Price chart
            price_chart = self.create_price_chart(properties)
            if price_chart:
                story.append(Paragraph("Price Analysis", self.styles['CustomHeading']))
                img = Image(price_chart, width=6*inch, height=3.5*inch)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
            
            # Location chart
            location_chart = self.create_location_chart(properties)
            if location_chart:
                story.append(PageBreak())
                story.append(Paragraph("Location Distribution", self.styles['CustomHeading']))
                img = Image(location_chart, width=6*inch, height=4*inch)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
        
        # Property Details
        story.append(PageBreak())
        story.append(Paragraph("Property Listings", self.styles['CustomHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        # Show top properties
        top_properties = properties[:20]  # Limit to 20 for PDF size
        
        for i, prop in enumerate(top_properties, 1):
            # Property header
            prop_title = f"{i}. {prop.get('location', 'Unknown Location')} - ${prop.get('price', 0):,.0f}"
            story.append(Paragraph(f"<b>{prop_title}</b>", self.styles['CustomBody']))
            
            # Property details
            details = []
            details.append(f"<b>Property ID:</b> {prop.get('property_id', 'N/A')}")
            details.append(f"<b>Status:</b> {prop.get('status', 'N/A')}")
            
            if prop.get('long_description'):
                desc = prop['long_description'][:200] + '...' if len(prop['long_description']) > 200 else prop['long_description']
                details.append(f"<b>Description:</b> {desc}")
            
            for detail in details:
                story.append(Paragraph(detail, self.styles['CustomBody']))
            
            story.append(Spacer(1, 0.15*inch))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        footer = Paragraph(
            "<i>This report was generated by the Real Estate Search Engine AI Assistant</i>",
            self.styles['CustomBody']
        )
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def generate_property_comparison_report(self, properties, filename='comparison_report.pdf'):
        """Generate a comparison report for selected properties"""
        os.makedirs('reports', exist_ok=True)
        filepath = os.path.join('reports', filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        
        # Title
        title = Paragraph("Property Comparison Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Date
        date_str = datetime.now().strftime("%B %d, %Y")
        meta = Paragraph(f"<i>Generated on {date_str}</i>", self.styles['CustomBody'])
        story.append(meta)
        story.append(Spacer(1, 0.3*inch))
        
        # Comparison table
        story.append(Paragraph("Property Comparison", self.styles['CustomHeading']))
        
        # Build comparison data
        table_data = [['Property ID', 'Location', 'Price', 'Status']]
        
        for prop in properties[:10]:  # Limit to 10 properties
            table_data.append([
                str(prop.get('property_id', 'N/A'))[:20],
                str(prop.get('location', 'N/A'))[:30],
                f"${prop.get('price', 0):,.0f}",
                str(prop.get('status', 'N/A'))
            ])
        
        comp_table = Table(table_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 1*inch])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(comp_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Price comparison chart
        if len(properties) > 1:
            story.append(Paragraph("Price Comparison", self.styles['CustomHeading']))
            
            fig, ax = plt.subplots(figsize=(8, 5))
            prop_names = [f"Property {i+1}" for i in range(min(10, len(properties)))]
            prices = [p.get('price', 0) for p in properties[:10]]
            
            ax.bar(prop_names, prices, color='#4a90e2', alpha=0.7)
            ax.set_ylabel('Price ($)', fontsize=12)
            ax.set_title('Price Comparison', fontsize=14, fontweight='bold')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(axis='y', alpha=0.3)
            
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            img = Image(img_buffer, width=6*inch, height=3.5*inch)
            story.append(img)
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def generate_custom_report(self, title, content, charts=None, filename='custom_report.pdf'):
        """Generate a custom report with provided content"""
        os.makedirs('reports', exist_ok=True)
        filepath = os.path.join('reports', filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        
        # Title
        report_title = Paragraph(title, self.styles['CustomTitle'])
        story.append(report_title)
        story.append(Spacer(1, 0.3*inch))
        
        # Content
        for item in content:
            if item['type'] == 'heading':
                story.append(Paragraph(item['text'], self.styles['CustomHeading']))
            elif item['type'] == 'paragraph':
                story.append(Paragraph(item['text'], self.styles['CustomBody']))
            elif item['type'] == 'spacer':
                story.append(Spacer(1, item.get('height', 0.2)*inch))
        
        # Add charts if provided
        if charts:
            for chart in charts:
                story.append(PageBreak())
                story.append(Paragraph(chart.get('title', 'Chart'), self.styles['CustomHeading']))
                img = Image(chart['image'], width=6*inch, height=4*inch)
                story.append(img)
        
        # Build PDF
        doc.build(story)
        
        return filepath
